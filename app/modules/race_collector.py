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
    async def _fetch_jra_race_detail(self, session: aiohttp.ClientSession, race: Dict) -> Dict:
        """JRA公式レース詳細取得"""
        try:
            race_id = race.get('race_id', '')
            if not race_id:
                return {}
            
            url = f"{Config.JRA_BASE_URL}/race/detail/{race_id}"
            
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_jra_race_detail(html)
                    
        except Exception as e:
            logger.error(f"JRA race detail error: {str(e)}")
        
        return {}

    async def _fetch_netkeiba_race_detail(self, session: aiohttp.ClientSession, race: Dict) -> Dict:
        """netkeibaレース詳細取得"""
        try:
            race_url = race.get('race_url', '')
            if not race_url:
                return {}
            
            async with session.get(race_url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_netkeiba_race_detail(html)
                    
        except Exception as e:
            logger.error(f"Netkeiba race detail error: {str(e)}")
        
        return {}

    def _parse_jra_race_detail(self, html: str) -> Dict:
        """JRA公式レース詳細解析"""
        detail = {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 出走馬情報
            horses = []
            horse_table = soup.find('table', class_='horse-table')
            if horse_table:
                rows = horse_table.find_all('tr')[1:]  # ヘッダー除く
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 10:
                        horse_info = {
                            'barrier': cells[0].text.strip(),
                            'horse_number': cells[1].text.strip(),
                            'horse_name': cells[2].text.strip(),
                            'age': cells[3].text.strip(),
                            'sex': cells[4].text.strip(),
                            'weight': cells[5].text.strip(),
                            'jockey': cells[6].text.strip(),
                            'trainer': cells[7].text.strip(),
                            'owner': cells[8].text.strip(),
                            'odds': cells[9].text.strip() if len(cells) > 9 else '',
                        }
                        horses.append(horse_info)
            
            detail['horses'] = horses
            
            # レース条件
            condition_div = soup.find('div', class_='race-condition')
            if condition_div:
                detail['condition'] = condition_div.text.strip()
            
            # 天候・馬場状態
            weather_div = soup.find('div', class_='weather')
            if weather_div:
                detail['weather'] = weather_div.text.strip()
                
        except Exception as e:
            logger.error(f"JRA detail parsing error: {str(e)}")
        
        return detail

    def _parse_netkeiba_race_detail(self, html: str) -> Dict:
        """netkeibaレース詳細解析"""
        detail = {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 出走表解析
            shutuba_table = soup.find('table', class_='race_table_01')
            if shutuba_table:
                horses = []
                rows = shutuba_table.find_all('tr', class_='HorseList')
                
                for row in rows:
                    horse_data = self._extract_netkeiba_horse_data(row)
                    if horse_data:
                        horses.append(horse_data)
                
                detail['horses'] = horses
            
            # 血統情報
            pedigree_data = self._extract_pedigree_data(soup)
            if pedigree_data:
                detail['bloodlines'] = pedigree_data
            
            # 過去成績
            past_performances = self._extract_past_performances(soup)
            if past_performances:
                detail['past_performances'] = past_performances
                
        except Exception as e:
            logger.error(f"Netkeiba detail parsing error: {str(e)}")
        
        return detail

    def _extract_netkeiba_horse_data(self, row) -> Optional[Dict]:
        """netkeiba馬データ抽出"""
        try:
            cells = row.find_all('td')
            if len(cells) < 15:
                return None
            
            return {
                'barrier': cells[0].text.strip(),
                'horse_number': cells[1].text.strip(),
                'horse_name': cells[3].find('a').text.strip() if cells[3].find('a') else '',
                'age': cells[4].text.strip(),
                'sex': cells[4].text.strip(),
                'weight': cells[5].text.strip(),
                'jockey': cells[6].find('a').text.strip() if cells[6].find('a') else '',
                'trainer': cells[7].find('a').text.strip() if cells[7].find('a') else '',
                'odds': cells[12].text.strip(),
                'popularity': cells[13].text.strip(),
            }
            
        except Exception as e:
            logger.error(f"Horse data extraction error: {str(e)}")
            return None

    def _extract_pedigree_data(self, soup) -> Dict:
        """血統データ抽出"""
        pedigree = {}
        
        try:
            # 血統表の解析（実装省略）
            pedigree_table = soup.find('table', class_='blood_table')
            if pedigree_table:
                # 3代血統の抽出
                pedigree = {
                    'father': '',
                    'mother': '',
                    'father_father': '',
                    'father_mother': '',
                    'mother_father': '',
                    'mother_mother': '',
                }
                
        except Exception as e:
            logger.error(f"Pedigree extraction error: {str(e)}")
        
        return pedigree

    def _extract_past_performances(self, soup) -> List[Dict]:
        """過去成績抽出"""
        performances = []
        
        try:
            # 過去成績表の解析（実装省略）
            past_table = soup.find('table', class_='db_h_race_results')
            if past_table:
                rows = past_table.find_all('tr')[1:]  # ヘッダー除く
                
                for row in rows:
                    # 各レースの成績データ抽出
                    pass
                    
        except Exception as e:
            logger.error(f"Past performance extraction error: {str(e)}")
        
        return performances

    async def _fetch_additional_race_info(self, session: aiohttp.ClientSession, race: Dict) -> Dict:
        """追加情報収集（keibalab, umanity等）"""
        additional_info = {}
        
        try:
            # keibalab から統計情報
            keibalab_info = await self._fetch_keibalab_info(session, race)
            additional_info.update(keibalab_info)
            
            # umanity からAI分析
            umanity_info = await self._fetch_umanity_info(session, race)
            additional_info.update(umanity_info)
            
        except Exception as e:
            logger.error(f"Additional info collection error: {str(e)}")
        
        return additional_info

    async def _fetch_keibalab_info(self, session: aiohttp.ClientSession, race: Dict) -> Dict:
        """keibalab情報取得"""
        # 実装省略（実際のAPIに合わせて実装）
        return {
            'statistics': {},
            'trends': {}
        }

    async def _fetch_umanity_info(self, session: aiohttp.ClientSession, race: Dict) -> Dict:
        """umanity AI分析取得"""
        # 実装省略（実際のAPIに合わせて実装）
        return {
            'ai_prediction': {},
            'confidence_score': 0
        }

    async def _validate_and_fix_encoding(self, race_data: List[Dict]) -> List[Dict]:
        """文字化け検証・修復"""
        validated_data = []
        
        for race in race_data:
            validated_race = await self._fix_single_race_encoding(race)
            if validated_race:
                validated_data.append(validated_race)
        
        return validated_data

    async def _fix_single_race_encoding(self, race_data: Dict) -> Optional[Dict]:
        """単一レースの文字化け修復"""
        try:
            fixed_race = race_data.copy()
            
            # 文字化け検出・修復
            for key, value in race_data.items():
                if isinstance(value, str):
                    fixed_value = self._fix_encoding_string(value)
                    fixed_race[key] = fixed_value
                elif isinstance(value, list):
                    fixed_list = []
                    for item in value:
                        if isinstance(item, dict):
                            fixed_item = await self._fix_single_race_encoding(item)
                            if fixed_item:
                                fixed_list.append(fixed_item)
                        else:
                            fixed_list.append(item)
                    fixed_race[key] = fixed_list
            
            return fixed_race
            
        except Exception as e:
            logger.error(f"Encoding fix error: {str(e)}")
            return None

    def _fix_encoding_string(self, text: str) -> str:
        """文字列の文字化け修復"""
        if not text:
            return text
        
        try:
            # 日本語文字範囲チェック
            if self._is_valid_japanese_text(text):
                return text
            
            # 文字化け修復試行
            for encoding in Config.ENCODING_PRIORITY:
                try:
                    # エンコーディング変換試行
                    bytes_data = text.encode('latin1')
                    decoded_text = bytes_data.decode(encoding)
                    
                    if self._is_valid_japanese_text(decoded_text):
                        return decoded_text
                        
                except (UnicodeDecodeError, UnicodeEncodeError):
                    continue
            
            # 修復不可の場合は元の文字列を返す
            return text
            
        except Exception as e:
            logger.error(f"String encoding fix error: {str(e)}")
            return text

    def _is_valid_japanese_text(self, text: str) -> bool:
        """日本語テキストの妥当性チェック"""
        if not text:
            return True
        
        # 日本語文字範囲チェック
        japanese_ranges = [
            (0x3040, 0x309F),  # ひらがな
            (0x30A0, 0x30FF),  # カタカナ
            (0x4E00, 0x9FAF),  # 漢字
            (0xFF00, 0xFFEF),  # 全角英数字
        ]
        
        japanese_char_count = 0
        total_chars = len(text)
        
        for char in text:
            char_code = ord(char)
            for start, end in japanese_ranges:
                if start <= char_code <= end:
                    japanese_char_count += 1
                    break
        
        # 日本語文字が50%以上含まれていれば有効とみなす
        return (japanese_char_count / total_chars) >= 0.5 if total_chars > 0 else True

    def _assess_data_quality(self, race_data: List[Dict]) -> Dict[str, Any]:
        """データ品質評価"""
        if not race_data:
            return {
                'overall_quality': 0.0,
                'required_completeness': 0.0,
                'recommended_completeness': 0.0,
                'encoding_quality': 0.0,
                'errors': ['No race data collected']
            }
        
        total_required_score = 0
        total_recommended_score = 0
        total_encoding_score = 0
        errors = []
        
        for race in race_data:
            # 必須フィールド完全性チェック
            required_completeness = self._check_field_completeness(race, self.required_fields)
            total_required_score += required_completeness
            
            # 推奨フィールド完全性チェック
            recommended_completeness = self._check_field_completeness(race, self.recommended_fields)
            total_recommended_score += recommended_completeness
            
            # 文字化け品質チェック
            encoding_quality = self._check_encoding_quality(race)
            total_encoding_score += encoding_quality
            
            if required_completeness < 1.0:
                errors.append(f"Race {race.get('race_name', 'Unknown')}: Required fields incomplete")
        
        race_count = len(race_data)
        avg_required = total_required_score / race_count
        avg_recommended = total_recommended_score / race_count
        avg_encoding = total_encoding_score / race_count
        
        # 総合品質スコア
        overall_quality = (avg_required * 0.5 + avg_recommended * 0.3 + avg_encoding * 0.2)
        
        return {
            'overall_quality': overall_quality,
            'required_completeness': avg_required,
            'recommended_completeness': avg_recommended,
            'encoding_quality': avg_encoding,
            'race_count': race_count,
            'errors': errors
        }

    def _check_field_completeness(self, race_data: Dict, fields: List[str]) -> float:
        """フィールド完全性チェック"""
        completed_fields = 0
        
        for field in fields:
            if field in race_data and race_data[field]:
                completed_fields += 1
        
        return completed_fields / len(fields) if fields else 1.0

    def _check_encoding_quality(self, race_data: Dict) -> float:
        """文字化け品質チェック"""
        text_fields = ['race_name', 'track', 'condition']
        valid_fields = 0
        
        for field in text_fields:
            if field in race_data:
                text = str(race_data[field])
                if self._is_valid_japanese_text(text):
                    valid_fields += 1
        
        return valid_fields / len(text_fields) if text_fields else 1.0

    async def collect_specific_race(self, race_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """特定レース情報収集"""
        try:
            # 簡易的な特定レース収集（実装省略）
            return {
                'race_name': race_info.get('race_name', '指定レース'),
                'horses': [],
                'basic_info': race_info
            }
            
        except Exception as e:
            logger.error(f"Specific race collection error: {str(e)}")
            return None
