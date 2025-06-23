import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AbilityMetrics:
    """実戦能力指標データクラス"""
    horse_name: str
    speed_ability: float
    stamina_ability: float
    acceleration_ability: float
    cornering_ability: float
    racing_sense: float
    pressure_resistance: float
    seasonal_form: float
    class_performance: float
    ability_score: float

class AbilityAnalysis:
    """実戦能力分析システム v3.1【18%重み・季節適性評価追加】"""
    
    def __init__(self):
        self.max_analysis_time = 50  # 秒
        self.weight_in_system = 0.18  # システム全体の18%重み
        
        # 能力評価の重み配分
        self.ability_weights = {
            'speed_ability': 0.25,        # スピード能力
            'stamina_ability': 0.20,      # スタミナ能力
            'acceleration_ability': 0.15,  # 加速力
            'cornering_ability': 0.10,    # コーナリング
            'racing_sense': 0.10,         # レースセンス
            'pressure_resistance': 0.10,   # プレッシャー耐性
            'seasonal_form': 0.10         # 季節適性
        }
        
        # 季節適性パターン
        self.seasonal_patterns = {
            'spring_type': {'3月': 1.2, '4月': 1.1, '5月': 1.0, '夏': 0.8, '秋': 0.9, '冬': 0.7},
            'summer_type': {'春': 0.8, '6月': 1.0, '7月': 1.2, '8月': 1.3, '9月': 1.1, '秋冬': 0.7},
            'autumn_type': {'春夏': 0.8, '9月': 1.0, '10月': 1.2, '11月': 1.1, '12月': 1.0, '冬': 0.9},
            'winter_type': {'春夏': 0.7, '秋': 0.9, '12月': 1.1, '1月': 1.2, '2月': 1.1},
            'all_weather': {'通年': 1.0}
        }
        
        # クラス別期待値
        self.class_expectations = {
            'G1': {'win_rate': 0.067, 'place_rate': 0.20},
            'G2': {'win_rate': 0.083, 'place_rate': 0.25},
            'G3': {'win_rate': 0.100, 'place_rate': 0.30},
            'OP': {'win_rate': 0.125, 'place_rate': 0.35},
            '3勝': {'win_rate': 0.167, 'place_rate': 0.40},
            '2勝': {'win_rate': 0.200, 'place_rate': 0.45},
            '1勝': {'win_rate': 0.250, 'place_rate': 0.50},
            'maiden': {'win_rate': 0.333, 'place_rate': 0.60}
        }

    async def analyze(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """実戦能力分析実行（50秒・18%重み）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting ability analysis v3.1 with seasonal adaptation")
        
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return self._create_error_result("No horses data")
            
            # レース条件取得
            race_conditions = self._extract_race_conditions(race_data)
            current_season = self._determine_current_season()
            
            # 各馬の実戦能力分析
            ability_analyses = await self._analyze_all_horses_ability(
                horses, race_conditions, current_season
            )
            
            # 能力ランキング作成
            ability_ranking = self._create_ability_ranking(ability_analyses)
            
            # 能力的注目馬抽出
            notable_abilities = self._identify_notable_abilities(ability_analyses)
            
            # 季節適性特別分析
            seasonal_analysis = self._analyze_seasonal_adaptability(ability_analyses, current_season)
            
            # クラス別実戦能力評価
            class_performance_analysis = self._analyze_class_performance(ability_analyses, race_conditions)
            
            # 総合実戦能力スコア
            overall_score = self._calculate_overall_ability_score(ability_analyses)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Ability analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'ability_score': overall_score,
                'horse_ability_analyses': ability_analyses,
                'ability_ranking': ability_ranking,
                'notable_abilities': notable_abilities,
                'seasonal_analysis': seasonal_analysis,
                'class_performance_analysis': class_performance_analysis,
                'race_ability_summary': self._create_race_ability_summary(
                    ability_analyses, race_conditions, current_season
                )
            }
            
        except Exception as e:
            logger.error(f"Ability analysis error: {str(e)}")
            return self._create_error_result(str(e))

    async def _analyze_all_horses_ability(self, horses: List[Dict], race_conditions: Dict[str, Any], 
                                        current_season: str) -> List[Dict[str, Any]]:
        """全馬実戦能力分析"""
        ability_analyses = []
        
        # 並行処理でパフォーマンス向上
        semaphore = asyncio.Semaphore(3)  # 同時実行数制限
        
        tasks = [
            self._analyze_single_horse_ability(horse, race_conditions, current_season, semaphore)
            for horse in horses
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Single horse ability analysis error: {result}")
                continue
            if result:
                ability_analyses.append(result)
        
        return ability_analyses

    async def _analyze_single_horse_ability(self, horse: Dict[str, Any], race_conditions: Dict[str, Any], 
                                          current_season: str, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """単一馬実戦能力分析"""
        async with semaphore:
            try:
                horse_name = horse.get('horse_name', '')
                
                # 過去成績データ取得
                past_performances = await self._get_past_performances(horse)
                
                # スピード能力分析（25%重み）
                speed_ability = await self._analyze_speed_ability(past_performances, race_conditions)
                
                # スタミナ能力分析（20%重み）
                stamina_ability = await self._analyze_stamina_ability(past_performances, race_conditions)
                
                # 加速力分析（15%重み）
                acceleration_ability = await self._analyze_acceleration_ability(past_performances)
                
                # コーナリング能力分析（10%重み）
                cornering_ability = await self._analyze_cornering_ability(past_performances, race_conditions)
                
                # レースセンス分析（10%重み）
                racing_sense = await self._analyze_racing_sense(past_performances)
                
                # プレッシャー耐性分析（10%重み）
                pressure_resistance = await self._analyze_pressure_resistance(past_performances, race_conditions)
                
                # 季節適性分析（10%重み）
                seasonal_form = await self._analyze_seasonal_form(past_performances, current_season)
                
                # クラス別実績分析
                class_performance = await self._analyze_class_performance_single(past_performances, race_conditions)
                
                # 総合実戦能力スコア計算
                ability_score = self._calculate_horse_ability_score(
                    speed_ability, stamina_ability, acceleration_ability,
                    cornering_ability, racing_sense, pressure_resistance, seasonal_form
                )
                
                return {
                    'horse_name': horse_name,
                    'speed_ability': speed_ability,
                    'stamina_ability': stamina_ability,
                    'acceleration_ability': acceleration_ability,
                    'cornering_ability': cornering_ability,
                    'racing_sense': racing_sense,
                    'pressure_resistance': pressure_resistance,
                    'seasonal_form': seasonal_form,
                    'class_performance': class_performance,
                    'ability_score': ability_score,
                    'ability_rating': self._score_to_rating(ability_score),
                    'ability_strengths': self._identify_ability_strengths(
                        speed_ability, stamina_ability, acceleration_ability,
                        cornering_ability, racing_sense, pressure_resistance
                    ),
                    'seasonal_compatibility': self._evaluate_seasonal_compatibility(seasonal_form, current_season)
                }
                
            except Exception as e:
                logger.error(f"Single horse ability analysis error: {str(e)}")
                return self._create_default_ability_analysis(horse.get('horse_name', ''))

    async def _get_past_performances(self, horse: Dict[str, Any]) -> List[Dict[str, Any]]:
        """過去成績取得"""
        try:
            # 実際の実装では外部APIやデータベースから取得
            # ここでは模擬データを使用
            
            horse_name = horse.get('horse_name', '')
            
            # 模擬過去成績データ
            past_performances = []
            for i in range(5):  # 直近5走
                performance = {
                    'race_date': (datetime.now() - timedelta(days=30*(i+1))).strftime('%Y-%m-%d'),
                    'race_name': f'過去レース{i+1}',
                    'finish_position': min(18, max(1, 3 + i)),
                    'horse_count': 16,
                    'distance': 1600 + (i * 200),
                    'surface': '芝' if i % 2 == 0 else 'ダート',
                    'time': f"1:{35 + i}:{20 + (i*5)}",
                    'last_3f': f"{35 + i}.{i}",
                    'weight_carried': 56.0,
                    'jockey': f'騎手{i+1}',
                    'odds': 5.0 + i,
                    'margin': f"{i*0.5}",
                    'pace': 'M' if i % 2 == 0 else 'S',
                    'running_style': self._determine_running_style(i),
                    'race_grade': 'G3' if i == 0 else 'OP' if i == 1 else '3勝'
                }
                past_performances.append(performance)
            
            return past_performances
            
        except Exception as e:
            logger.error(f"Past performances retrieval error: {str(e)}")
            return []

    async def _analyze_speed_ability(self, past_performances: List[Dict], race_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """スピード能力分析（25%重み）"""
        try:
            if not past_performances:
                return {'speed_score': 50.0, 'speed_rating': 'average'}
            
            # タイム分析
            time_scores = []
            for performance in past_performances[:3]:  # 直近3走
                time_score = self._calculate_time_score(performance, race_conditions)
                time_scores.append(time_score)
            
            # 上がり3F分析
            last_3f_scores = []
            for performance in past_performances[:3]:
                last_3f_score = self._calculate_last_3f_score(performance)
                last_3f_scores.append(last_3f_score)
            
            # 平均スピードスコア
            avg_time_score = sum(time_scores) / len(time_scores) if time_scores else 50.0
            avg_last_3f_score = sum(last_3f_scores) / len(last_3f_scores) if last_3f_scores else 50.0
            
            # 総合スピード能力スコア
            speed_score = (avg_time_score * 0.6 + avg_last_3f_score * 0.4)
            
            return {
                'speed_score': speed_score,
                'speed_rating': self._score_to_rating(speed_score),
                'time_analysis': {
                    'average_time_score': avg_time_score,
                    'time_consistency': self._calculate_consistency(time_scores)
                },
                'last_3f_analysis': {
                    'average_last_3f_score': avg_last_3f_score,
                    'kick_ability': max(last_3f_scores) if last_3f_scores else 50.0
                },
                'speed_trend': self._analyze_speed_trend(time_scores)
            }
            
        except Exception as e:
            logger.error(f"Speed ability analysis error: {str(e)}")
            return {'speed_score': 50.0, 'speed_rating': 'average'}

    async def _analyze_stamina_ability(self, past_performances: List[Dict], race_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """スタミナ能力分析（20%重み）"""
        try:
            target_distance = race_conditions.get('distance', 1600)
            
            # 距離別成績分析
            distance_performances = []
            for performance in past_performances:
                race_distance = performance.get('distance', 1600)
                if abs(race_distance - target_distance) <= 400:  # ±400m以内
                    distance_performances.append(performance)
            
            if not distance_performances:
                distance_performances = past_performances[:3]  # フォールバック
            
            # スタミナスコア計算
            stamina_scores = []
            for performance in distance_performances:
                stamina_score = self._calculate_stamina_score(performance, target_distance)
                stamina_scores.append(stamina_score)
            
            avg_stamina_score = sum(stamina_scores) / len(stamina_scores) if stamina_scores else 50.0
            
            # 距離延長・短縮への対応力
            distance_adaptability = self._analyze_distance_adaptability(past_performances, target_distance)
            
            # 総合スタミナ能力
            stamina_ability_score = (avg_stamina_score * 0.7 + distance_adaptability * 0.3)
            
            return {
                'stamina_score': stamina_ability_score,
                'stamina_rating': self._score_to_rating(stamina_ability_score),
                'distance_adaptability': distance_adaptability,
                'optimal_distance': self._determine_optimal_distance(past_performances),
                'stamina_consistency': self._calculate_consistency(stamina_scores)
            }
            
        except Exception as e:
            logger.error(f"Stamina ability analysis error: {str(e)}")
            return {'stamina_score': 50.0, 'stamina_rating': 'average'}

    async def _analyze_acceleration_ability(self, past_performances: List[Dict]) -> Dict[str, Any]:
        """加速力分析（15%重み）"""
        try:
            # 直線での伸び脚分析
            acceleration_scores = []
            
            for performance in past_performances[:3]:
                # 上がり3Fと着順の関係から加速力を推定
                last_3f = performance.get('last_3f', '36.0')
                finish_pos = performance.get('finish_position', 10)
                horse_count = performance.get('horse_count', 16)
                
                # 上がり3Fタイムを数値化
                try:
                    last_3f_seconds = float(last_3f.replace(':', '.'))
                except:
                    last_3f_seconds = 36.0
                
                # 加速力スコア計算（上がりタイムと着順の関係）
                time_score = max(0, 100 - (last_3f_seconds - 33.0) * 10)
                position_score = max(0, 100 - (finish_pos / horse_count * 100))
                
                acceleration_score = (time_score * 0.6 + position_score * 0.4)
                acceleration_scores.append(acceleration_score)
            
            avg_acceleration = sum(acceleration_scores) / len(acceleration_scores) if acceleration_scores else 50.0
            
            return {
                'acceleration_score': avg_acceleration,
                'acceleration_rating': self._score_to_rating(avg_acceleration),
                'kick_power': max(acceleration_scores) if acceleration_scores else 50.0,
                'acceleration_consistency': self._calculate_consistency(acceleration_scores)
            }
            
        except Exception as e:
            logger.error(f"Acceleration ability analysis error: {str(e)}")
            return {'acceleration_score': 50.0, 'acceleration_rating': 'average'}

    async def _analyze_seasonal_form(self, past_performances: List[Dict], current_season: str) -> Dict[str, Any]:
        """季節適性分析（10%重み）"""
        try:
            seasonal_scores = {}
            
            # 月別成績分析
            for performance in past_performances:
                race_date = performance.get('race_date', '')
                if race_date:
                    try:
                        month = datetime.strptime(race_date, '%Y-%m-%d').month
                        season = self._month_to_season(month)
                        
                        if season not in seasonal_scores:
                            seasonal_scores[season] = []
                        
                        # 成績スコア計算
                        finish_pos = performance.get('finish_position', 10)
                        horse_count = performance.get('horse_count', 16)
                        performance_score = max(0, 100 - (finish_pos / horse_count * 100))
                        
                        seasonal_scores[season].append(performance_score)
                    except:
                        continue
            
            # 現在の季節での適性評価
            current_season_score = 50.0
            if current_season in seasonal_scores:
                season_performances = seasonal_scores[current_season]
                current_season_score = sum(season_performances) / len(season_performances)
            
            # 季節パターン判定
            seasonal_pattern = self._determine_seasonal_pattern(seasonal_scores)
            
            return {
                'seasonal_score': current_season_score,
                'seasonal_rating': self._score_to_rating(current_season_score),
                'seasonal_pattern': seasonal_pattern,
                'seasonal_scores': seasonal_scores,
                'current_season': current_season,
                'seasonal_compatibility': self._evaluate_seasonal_compatibility(current_season_score, current_season)
            }
            
        except Exception as e:
            logger.error(f"Seasonal form analysis error: {str(e)}")
            return {'seasonal_score': 50.0, 'seasonal_rating': 'average'}

    def _calculate_horse_ability_score(self, speed_ability: Dict, stamina_ability: Dict, 
                                     acceleration_ability: Dict, cornering_ability: Dict,
                                     racing_sense: Dict, pressure_resistance: Dict, 
                                     seasonal_form: Dict) -> float:
        """馬の実戦能力総合スコア計算"""
        try:
            speed_score = speed_ability.get('speed_score', 50.0)
            stamina_score = stamina_ability.get('stamina_score', 50.0)
            acceleration_score = acceleration_ability.get('acceleration_score', 50.0)
            cornering_score = cornering_ability.get('cornering_score', 50.0)
            sense_score = racing_sense.get('sense_score', 50.0)
            pressure_score = pressure_resistance.get('pressure_score', 50.0)
            seasonal_score = seasonal_form.get('seasonal_score', 50.0)
            
            # 重み付き計算
            total_score = (
                speed_score * self.ability_weights['speed_ability'] +
                stamina_score * self.ability_weights['stamina_ability'] +
                acceleration_score * self.ability_weights['acceleration_ability'] +
                cornering_score * self.ability_weights['cornering_ability'] +
                sense_score * self.ability_weights['racing_sense'] +
                pressure_score * self.ability_weights['pressure_resistance'] +
                seasonal_score * self.ability_weights['seasonal_form']
            )
            
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"Horse ability score calculation error: {str(e)}")
            return 50.0

    # ヘルパーメソッド（実装省略、実際の開発時に詳細実装）
    def _extract_race_conditions(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """レース条件抽出"""
        return {
            'distance': race_data.get('distance', 1600),
            'surface': race_data.get('surface', '芝'),
            'track': race_data.get('track', '中山'),
            'grade': race_data.get('grade', 'OP')
        }

    def _determine_current_season(self) -> str:
        """現在の季節判定"""
        month = datetime.now().month
        return self._month_to_season(month)

    def _month_to_season(self, month: int) -> str:
        """月から季節への変換"""
        if month in [3, 4, 5]:
            return '春'
        elif month in [6, 7, 8]:
            return '夏'
        elif month in [9, 10, 11]:
            return '秋'
        else:
            return '冬'

    def _score_to_rating(self, score: float) -> str:
        """スコアを評価に変換"""
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 55:
            return 'average'
        elif score >= 40:
            return 'poor'
        else:
            return 'very_poor'

    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """エラー結果作成"""
        return {
            'status': 'error',
            'error_message': error_msg,
            'ability_score': 0,
            'execution_time': 0
        }

    # ... その他のヘルパーメソッドは実装省略
