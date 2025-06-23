import aiohttp
import asyncio
import logging
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import chardet

from ..config import Config

logger = logging.getLogger(__name__)

class RaceCollector:
    """レース情報収集システム v3.1【プロモード専用最適化完全版】"""
    
    def __init__(self):
        self.max_collection_time = 75  # 秒
        self.required_data_rate = 1.0  # 100%必須
        self.recommended_data_rate = 0.95  # 95%推奨
        
        # データソース設定
        self.data_sources = {
            'jra_official': {
                'url': Config.JRA_BASE_URL,
                'priority': 1,
                'reliability': 1.0,
                'encoding': 'utf-8'
            },
            'netkeiba': {
                'url': Config.NETKEIBA_BASE_URL,
                'priority': 2,
                'reliability': 0.95,
                'encoding': 'utf-8'
            },
            'keibalab': {
                'url': Config.KEIBALAB_BASE_URL,
                'priority': 3,
                'reliability': 0.90,
                'encoding': 'utf-8'
            },
            'umanity': {
                'url': Config.UMANITY_BASE_URL,
                'priority': 4,
                'reliability': 0.85,
                'encoding': 'utf-8'
            },
            'uma_x': {
                'url': Config.UMA_X_BASE_URL,
                'priority': 5,
                'reliability': 0.80,
                'encoding': 'utf-8'
            },
            'muryou_keiba_ai': {
                'url': Config.MURYOU_KEIBA_AI_BASE_URL,
                'priority': 6,
                'reliability': 0.75,
                'encoding': 'utf-8'
            }
        }
        
        # 必須データ項目（100%必須）
        self.required_fields = [
            'race_name', 'grade', 'track', 'course', 'distance',
            'surface', 'condition', 'weather', 'start_time',
            'horse_count', 'horses', 'jockeys', 'trainers'
        ]
        
        # 推奨データ項目（95%以上推奨）
        self.recommended_fields = [
            'past_performances', 'bloodlines', 'odds', 'popularity',
            'weight', 'barrier', 'age', 'sex', 'owner', 'breeder'
        ]

    async def collect_all_races(self) -> Dict[str, Any]:
        """全レース情報収集（75秒以内）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting race data collection v3.1")
        
        try:
            # 今日の開催情報取得
            today_races = await self._get_today_races()
            
            if not today_races:
                logger.warning("No races found for today")
                return {}
            
            # 各レースの詳細情報収集（並行処理）
            race_data = await self._collect_race_details(today_races)
            
            # 文字化け対策・品質検証
            validated_data = await self._validate_and_fix_encoding(race_data)
            
            # 品質チェック
            quality_report = self._assess_data_quality(validated_data)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"Data collection completed in {execution_time:.2f}s")
            
            if quality_report['overall_quality'] < 0.94:  # 94%未満は中止
                logger.error(f"Data quality insufficient: {quality_report['overall_quality']:.2%}")
                return {}
            
            return {
                'races': validated_data,
                'quality_report': quality_report,
                'collection_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Race collection error: {str(e)}")
            return {}

    async def _get_today_races(self) -> List[Dict[str, Any]]:
        """今日の開催レース一覧取得"""
        today = datetime.now().strftime('%Y%m%d')
        
        try:
            async with aiohttp.ClientSession() as session:
                # JRA公式から開催情報取得
                jra_races = await self._fetch_jra_races(session, today)
                
                # 補助ソースからも情報収集
                netkeiba_races = await self._fetch_netkeiba_races(session, today)
                
                # 情報統合
                combined_races = self._merge_race_lists(jra_races, netkeiba_races)
                
                logger.info(f"Found {len(combined_races)} races for {today}")
                return combined_races
                
        except Exception as e:
            logger.error(f"Error getting today's races: {str(e)}")
            return []

    async def _fetch_jra_races(self, session: aiohttp.ClientSession, date: str) -> List[Dict[str, Any]]:
        """JRA公式からレース情報取得"""
        try:
            # JRA公式API（実際のURLは適宜調整）
            url = f"{Config.JRA_BASE_URL}/race/calendar/{date}"
            
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_jra_race_list(html)
                else:
                    logger.warning(f"JRA API returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"JRA fetch error: {str(e)}")
            return []

    async def _fetch_netkeiba_races(self, session: aiohttp.ClientSession, date: str) -> List[Dict[str, Any]]:
        """netkeibaからレース情報取得"""
        try:
            url = f"{Config.NETKEIBA_BASE_URL}/race/list/{date}/"
            
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_netkeiba_race_list(html)
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Netkeiba fetch error: {str(e)}")
            return []

    def _parse_jra_race_list(self, html: str) -> List[Dict[str, Any]]:
        """JRA公式HTMLの解析"""
        races = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # レース情報を抽出（実際の構造に合わせて調整）
            race_elements = soup.find_all('div', class_='race-item')
            
            for element in race_elements:
                race_info = {
                    'source': 'jra_official',
                    'race_id': element.get('data-race-id', ''),
                    'race_name': element.find('h3').text.strip() if element.find('h3') else '',
                    'track': element.get('data-track', ''),
                    'race_number': element.get('data-race-number', ''),
                    'start_time': element.get('data-start-time', ''),
                    'grade': element.get('data-grade', ''),
                    'distance': element.get('data-distance', ''),
                    'surface': element.get('data-surface', ''),
                }
                
                if race_info['race_name']:  # 有効なレース名がある場合のみ追加
                    races.append(race_info)
                    
        except Exception as e:
            logger.error(f"JRA HTML parsing error: {str(e)}")
        
        return races

    def _parse_netkeiba_race_list(self, html: str) -> List[Dict[str, Any]]:
        """netkeibaHTMLの解析"""
        races = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # レース一覧を抽出
            race_links = soup.find_all('a', href=re.compile(r'/race/\d+/'))
            
            for link in race_links:
                race_info = {
                    'source': 'netkeiba',
                    'race_url': Config.NETKEIBA_BASE_URL + link.get('href', ''),
                    'race_name': link.text.strip(),
                }
                races.append(race_info)
                
        except Exception as e:
            logger.error(f"Netkeiba HTML parsing error: {str(e)}")
        
        return races

    def _merge_race_lists(self, jra_races: List[Dict], netkeiba_races: List[Dict]) -> List[Dict]:
        """レース情報の統合"""
        merged = []
        
        # JRAを基準とし、netkeibaで補完
        for jra_race in jra_races:
            race = jra_race.copy()
            
            # 同じレースをnetkeibaで検索して情報補完
            for netkeiba_race in netkeiba_races:
                if self._is_same_race(jra_race, netkeiba_race):
                    race.update(netkeiba_race)
                    break
            
            merged.append(race)
        
        return merged

    def _is_same_race(self, race1: Dict, race2: Dict) -> bool:
        """同一レース判定"""
        # レース名での簡易判定（実際はより複雑な判定が必要）
        name1 = race1.get('race_name', '').replace(' ', '').lower()
        name2 = race2.get('race_name', '').replace(' ', '').lower()
        
        return name1 and name2 and (name1 in name2 or name2 in name1)

    async def _collect_race_details(self, races: List[Dict]) -> List[Dict]:
        """各レースの詳細情報収集"""
        detailed_races = []
        
        # 並行処理でパフォーマンス向上
        semaphore = asyncio.Semaphore(5)  # 同時接続数制限
        
        tasks = [
            self._collect_single_race_detail(race, semaphore)
            for race in races
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Race detail collection error: {result}")
                continue
            if result:
                detailed_races.append(result)
        
        return detailed_races

    async def _collect_single_race_detail(self, race: Dict, semaphore: asyncio.Semaphore) -> Optional[Dict]:
        """単一レースの詳細情報収集"""
        async with semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    # 複数ソースから情報収集
                    race_detail = race.copy()
                    
                    # JRA公式詳細
                    if race.get('source') == 'jra_official':
                        jra_detail = await self._fetch_jra_race_detail(session, race)
                        race_detail.update(jra_detail)
                    
                    # netkeiba詳細
                    if race.get('race_url'):
                        netkeiba_detail = await self._fetch_netkeiba_race_detail(session, race)
                        race_detail.update(netkeiba_detail)
                    
                    # その他ソースからの情報収集
                    additional_info = await self._fetch_additional_race_info(session, race)
                    race_detail.update(additional_info)
                    
                    return race_detail
                    
            except Exception as e:
                logger.error(f"Single race detail error: {str(e)}")
                return None

    async def _fetch_jra_race_detail(self, session: aiohttp.ClientSession, race: Dict) -> Dict:
        """JRA公式レース詳細取得"""
        # 実装省略（実際のAPIに合わせて実装）
        return {
            'horses': [],
            'jockeys
