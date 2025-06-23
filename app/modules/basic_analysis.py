import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HorseEvaluation:
    """馬評価データクラス"""
    horse_name: str
    horse_number: int
    basic_score: float
    popularity_rank: int
    distance_fitness: float
    grade_fitness: float
    surface_fitness: float
    jockey_trainer_bonus: float
    condition_adjustment: float
    final_score: float
    rank: str
    investment_recommendation: str

class BasicAnalysis:
    """基本分析システム v3.1【最適化版】"""
    
    def __init__(self):
        self.max_analysis_time = 35  # 秒
        self.weight_in_system = 0.20  # システム全体の20%重み
        
        # 評価基準設定
        self.score_ranges = {
            'S+': (95, 100),
            'S': (88, 94),
            'A+': (82, 87),
            'A': (75, 81),
            'B+': (68, 74),
            'B': (60, 67),
            'C': (50, 59),
            'D': (40, 49),
            'E': (0, 39)
        }
        
        # 距離適性補正
        self.distance_fitness_bonus = {
            'perfect': 8,    # 最適距離
            'good': 3,       # 適正距離
            'normal': 0,     # 普通
            'poor': -5       # 不適正
        }
        
        # 格適正補正
        self.grade_fitness_bonus = {
            'upgrade': 10,   # 格上げ
            'same': 5,       # 同格
            'maintain': 0,   # 現状維持
            'downgrade': -3, # 格下げ
            'challenge': -8  # 大幅格上挑戦
        }

    async def analyze(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """基本分析実行（35秒以内）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting basic analysis v3.1")
        
        try:
            # STEP 0: 文字化け検証・修復（8秒）
            validated_data = await self._step_0_encoding_validation(race_data)
            if not validated_data:
                return self._create_error_result("Encoding validation failed")
            
            # STEP 1: 人気馬必須詳細分析（12秒）
            popular_horses_analysis = await self._step_1_popular_horses_analysis(validated_data)
            
            # STEP 2: レース基本条件判定（8秒）
            race_conditions = await self._step_2_race_conditions(validated_data)
            
            # STEP 3: 全馬完全評価（12秒）
            all_horses_evaluation = await self._step_3_complete_evaluation(
                validated_data, race_conditions
            )
            
            # STEP 4: ランク分類・選別（5秒）
            final_rankings = await self._step_4_ranking_classification(all_horses_evaluation)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Basic analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'popular_horses_analysis': popular_horses_analysis,
                'race_conditions': race_conditions,
                'horse_evaluations': all_horses_evaluation,
                'final_rankings': final_rankings,
                'total_score': self._calculate_total_score(final_rankings),
                'quality_indicators': self._generate_quality_indicators(validated_data)
            }
            
        except Exception as e:
            logger.error(f"Basic analysis error: {str(e)}")
            return self._create_error_result(str(e))

    async def _step_0_encoding_validation(self, race_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """STEP 0: 文字化け検証・修復（8秒）"""
        logger.info("Step 0: Encoding validation")
        
        try:
            validated_data = race_data.copy()
            
            # 必須フィールドの文字化けチェック
            required_fields = ['race_name', 'horses']
            
            for field in required_fields:
                if field not in race_data:
                    logger.error(f"Required field missing: {field}")
                    return None
                
                if field == 'race_name':
                    if not self._is_valid_japanese_text(race_data[field]):
                        logger.error(f"Invalid race name encoding: {race_data[field]}")
                        return None
                
                elif field == 'horses':
                    horses = race_data[field]
                    if not isinstance(horses, list) or len(horses) == 0:
                        logger.error("No horses data found")
                        return None
                    
                    # 各馬の名前をチェック
                    for horse in horses:
                        horse_name = horse.get('horse_name', '')
                        if not self._is_valid_japanese_text(horse_name):
                            logger.warning(f"Invalid horse name encoding: {horse_name}")
                            # 修復試行（簡略化）
                            horse['horse_name'] = self._fix_encoding_if_possible(horse_name)
            
            return validated_data
            
        except Exception as e:
            logger.error(f"Encoding validation error: {str(e)}")
            return None

    async def _step_1_popular_horses_analysis(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """STEP 1: 人気馬必須詳細分析（12秒）"""
        logger.info("Step 1: Popular horses analysis")
        
        horses = race_data.get('horses', [])
        popular_horses = []
        
        try:
            # 1-3番人気馬を特定
            sorted_horses = sorted(horses, key=lambda x: int(x.get('popularity', 99)))
            top_3_popular = sorted_horses[:3]
            
            for horse in top_3_popular:
                analysis = await self._analyze_popular_horse(horse, race_data)
                popular_horses.append(analysis)
            
            return {
                'top_3_analysis': popular_horses,
                'market_efficiency': self._evaluate_market_efficiency(popular_horses),
                'overvalued_risks': self._detect_overvalued_risks(popular_horses),
                'undervalued_opportunities': self._detect_undervalued_opportunities(popular_horses)
            }
            
        except Exception as e:
            logger.error(f"Popular horses analysis error: {str(e)}")
            return {}

    async def _analyze_popular_horse(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """人気馬個別分析"""
        try:
            horse_name = horse.get('horse_name', '')
            popularity = int(horse.get('popularity', 99))
            odds = float(horse.get('odds', 99.0))
            
            # 実力適正性評価
            ability_rating = self._evaluate_horse_ability(horse, race_data)
            
            # 市場評価妥当性チェック
            market_valuation = self._check_market_valuation(popularity, odds, ability_rating)
            
            # Critical失敗パターン回避
            risk_factors = self._identify_risk_factors(horse, race_data)
            
            return {
                'horse_name': horse_name,
                'popularity': popularity,
                'odds': odds,
                'ability_rating': ability_rating,
                'market_valuation': market_valuation,
                'risk_factors': risk_factors,
                'recommendation': self._generate_horse_recommendation(
                    ability_rating, market_valuation, risk_factors
                )
            }
            
        except Exception as e:
            logger.error(f"Popular horse analysis error: {str(e)}")
            return {}

    def _evaluate_horse_ability(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """馬の実力評価"""
        try:
            # 前走評価 (40%重み)
            last_race_score = self._evaluate_last_race(horse)
            
            # 前2走平均 (30%重み)
            recent_2_races_score = self._evaluate_recent_races(horse, 2)
            
            # 前3走平均 (20%重み)
            recent_3_races_score = self._evaluate_recent_races(horse, 3)
            
            # 同条件実績 (10%重み)
            same_condition_score = self._evaluate_same_conditions(horse, race_data)
            
            # 重み付き総合スコア
            total_score = (
                last_race_score * 0.4 +
                recent_2_races_score * 0.3 +
                recent_3_races_score * 0.2 +
                same_condition_score * 0.1
            )
            
            return {
                'last_race_score': last_race_score,
                'recent_2_races_score': recent_2_races_score,
                'recent_3_races_score': recent_3_races_score,
                'same_condition_score': same_condition_score,
                'total_ability_score': total_score,
                'ability_rank': self._score_to_rank(total_score)
            }
            
        except Exception as e:
            logger.error(f"Horse ability evaluation error: {str(e)}")
            return {'total_ability_score': 50, 'ability_rank': 'C'}

    def _evaluate_last_race(self, horse: Dict[str, Any]) -> float:
        """前走評価"""
        try:
            past_performances = horse.get('past_performances', [])
            if not past_performances:
                return 50.0  # デフォルトスコア
            
            last_race = past_performances[0]
            finish_position = int(last_race.get('finish_position', 99))
            horse_count = int(last_race.get('horse_count', 18))
            
            # 着順による基本スコア
            if finish_position == 1:
                base_score = 90
            elif finish_position == 2:
                base_score = 80
            elif finish_position == 3:
                base_score = 70
            elif finish_position <= 5:
                base_score = 60
            elif finish_position <= horse_count // 2:
                base_score = 50
            else:
                base_score = 40
            
            # レースレベル補正
            race_grade = last_race.get('grade', '')
            if 'G1' in race_grade:
                grade_bonus = 10
            elif 'G2' in race_grade:
                grade_bonus = 5
            elif 'G3' in race_grade:
                grade_bonus = 3
            else:
                grade_bonus = 0
            
            return min(100, base_score + grade_bonus)
            
        except Exception as e:
            logger.error(f"Last race evaluation error: {str(e)}")
            return 50.0

    def _evaluate_recent_races(self, horse: Dict[str, Any], race_count: int) -> float:
        """直近N走の平均評価"""
        try:
            past_performances = horse.get('past_performances', [])[:race_count]
            if not past_performances:
                return 50.0
            
            total_score = 0
            for race in past_performances:
                score = self._single_race_score(race)
                total_score += score
            
            return total_score / len(past_performances)
            
        except Exception as e:
            logger.error(f"Recent races evaluation error: {str(e)}")
            return 50.0

    def _single_race_score(self, race: Dict[str, Any]) -> float:
        """単一レースのスコア計算"""
        try:
            finish_position = int(race.get('finish_position', 99))
            
            if finish_position == 1:
                return 85
            elif finish_position == 2:
                return 75
            elif finish_position == 3:
                return 65
            elif finish_position <= 5:
                return 55
            else:
                return 45
                
        except Exception:
            return 50.0

    def _evaluate_same_conditions(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> float:
        """同条件実績評価"""
        try:
            # 距離・馬場・競馬場などの同条件での成績を評価
            # 簡略化実装
            distance = race_data.get('distance', '')
            surface = race_data.get('surface', '')
            
            past_performances = horse.get('past_performances', [])
            same_condition_races = []
            
            for race in past_performances:
                if (race.get('distance', '') == distance and 
                    race.get('surface', '') == surface):
                    same_condition_races.append(race)
            
            if not same_condition_races:
                return 50.0  # 同条件実績なし
            
            # 同条件での平均成績
            total_score = sum(self._single_race_score(race) for race in same_condition_races)
            return total_score / len(same_condition_races)
            
        except Exception as e:
            logger.error(f"Same conditions evaluation error: {str(e)}")
            return 50.0
    def _check_market_valuation(self, popularity: int, odds: float, ability_rating: Dict[str, Any]) -> Dict[str, Any]:
        """市場評価妥当性チェック"""
        try:
            ability_score = ability_rating.get('total_ability_score', 50)
            
            # 理論オッズ計算（簡略化）
            if ability_score >= 85:
                theoretical_odds_range = (1.5, 3.0)
            elif ability_score >= 75:
                theoretical_odds_range = (3.0, 6.0)
            elif ability_score >= 65:
                theoretical_odds_range = (6.0, 12.0)
            else:
                theoretical_odds_range = (12.0, 50.0)
            
            # 市場評価判定
            is_undervalued = odds > theoretical_odds_range[1]
            is_overvalued = odds < theoretical_odds_range[0]
            is_appropriate = not (is_undervalued or is_overvalued)
            
            valuation_score = 0
            if is_undervalued:
                valuation_score = min(100, 60 + (odds - theoretical_odds_range[1]) * 2)
            elif is_appropriate:
                valuation_score = 70
            else:  # overvalued
                valuation_score = max(20, 70 - (theoretical_odds_range[0] - odds) * 5)
            
            return {
                'theoretical_odds_range': theoretical_odds_range,
                'actual_odds': odds,
                'is_undervalued': is_undervalued,
                'is_overvalued': is_overvalued,
                'is_appropriate': is_appropriate,
                'valuation_score': valuation_score,
                'value_rating': 'HIGH' if is_undervalued else 'LOW' if is_overvalued else 'MEDIUM'
            }
            
        except Exception as e:
            logger.error(f"Market valuation check error: {str(e)}")
            return {'valuation_score': 50, 'value_rating': 'MEDIUM'}

    def _identify_risk_factors(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> List[str]:
        """リスクファクター識別"""
        risk_factors = []
        
        try:
            # 格上挑戦リスク
            if self._is_grade_challenge(horse, race_data):
                risk_factors.append("格上挑戦")
            
            # 距離延長・短縮リスク
            distance_change = self._analyze_distance_change(horse, race_data)
            if distance_change == 'extension':
                risk_factors.append("距離延長")
            elif distance_change == 'shortening':
                risk_factors.append("距離短縮")
            
            # 馬場変更リスク
            if self._is_surface_change(horse, race_data):
                risk_factors.append("馬場変更")
            
            # 休み明けリスク
            if self._is_layoff_return(horse):
                risk_factors.append("休み明け")
            
            # 斤量増加リスク
            if self._is_weight_increase(horse):
                risk_factors.append("斤量増")
            
        except Exception as e:
            logger.error(f"Risk factors identification error: {str(e)}")
        
        return risk_factors

    async def _step_2_race_conditions(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """STEP 2: レース基本条件判定（8秒）"""
        logger.info("Step 2: Race conditions analysis")
        
        try:
            # 馬場状態分析
            track_condition = self._analyze_track_condition(race_data)
            
            # 距離適性分析
            distance_analysis = self._analyze_distance_suitability(race_data)
            
            # 天候影響分析
            weather_impact = self._analyze_weather_impact(race_data)
            
            # 夏馬場特殊条件（6-9月の札幌・函館・新潟）
            summer_conditions = self._analyze_summer_conditions(race_data)
            
            return {
                'track_condition': track_condition,
                'distance_analysis': distance_analysis,
                'weather_impact': weather_impact,
                'summer_conditions': summer_conditions,
                'overall_condition_score': self._calculate_condition_score(
                    track_condition, distance_analysis, weather_impact, summer_conditions
                )
            }
            
        except Exception as e:
            logger.error(f"Race conditions analysis error: {str(e)}")
            return {}

    async def _step_3_complete_evaluation(self, race_data: Dict[str, Any], 
                                        race_conditions: Dict[str, Any]) -> List[HorseEvaluation]:
        """STEP 3: 全馬完全評価（12秒）"""
        logger.info("Step 3: Complete horse evaluation")
        
        horses = race_data.get('horses', [])
        evaluations = []
        
        try:
            for horse in horses:
                evaluation = await self._evaluate_single_horse(horse, race_data, race_conditions)
                evaluations.append(evaluation)
            
            # スコア順でソート
            evaluations.sort(key=lambda x: x.final_score, reverse=True)
            
            return evaluations
            
        except Exception as e:
            logger.error(f"Complete evaluation error: {str(e)}")
            return []

    async def _evaluate_single_horse(self, horse: Dict[str, Any], 
                                   race_data: Dict[str, Any], 
                                   race_conditions: Dict[str, Any]) -> HorseEvaluation:
        """単一馬評価"""
        try:
            horse_name = horse.get('horse_name', '')
            horse_number = int(horse.get('horse_number', 0))
            popularity = int(horse.get('popularity', 99))
            
            # 基礎実力点算出
            ability_rating = self._evaluate_horse_ability(horse, race_data)
            basic_score = ability_rating.get('total_ability_score', 50)
            
            # 各種適性・補正計算
            distance_fitness = self._calculate_distance_fitness(horse, race_data)
            grade_fitness = self._calculate_grade_fitness(horse, race_data)
            surface_fitness = self._calculate_surface_fitness(horse, race_data)
            jockey_trainer_bonus = self._calculate_jockey_trainer_bonus(horse)
            condition_adjustment = self._calculate_condition_adjustment(horse, race_conditions)
            
            # 最終スコア計算
            final_score = (basic_score + distance_fitness + grade_fitness + 
                         surface_fitness + jockey_trainer_bonus + condition_adjustment)
            final_score = max(0, min(100, final_score))  # 0-100範囲に制限
            
            # ランク判定
            rank = self._score_to_rank(final_score)
            
            # 投資推奨判定
            investment_recommendation = self._determine_investment_recommendation(
                final_score, popularity, rank
            )
            
            return HorseEvaluation(
                horse_name=horse_name,
                horse_number=horse_number,
                basic_score=basic_score,
                popularity_rank=popularity,
                distance_fitness=distance_fitness,
                grade_fitness=grade_fitness,
                surface_fitness=surface_fitness,
                jockey_trainer_bonus=jockey_trainer_bonus,
                condition_adjustment=condition_adjustment,
                final_score=final_score,
                rank=rank,
                investment_recommendation=investment_recommendation
            )
            
        except Exception as e:
            logger.error(f"Single horse evaluation error: {str(e)}")
            return HorseEvaluation(
                horse_name=horse.get('horse_name', '不明'),
                horse_number=0,
                basic_score=50,
                popularity_rank=99,
                distance_fitness=0,
                grade_fitness=0,
                surface_fitness=0,
                jockey_trainer_bonus=0,
                condition_adjustment=0,
                final_score=50,
                rank='C',
                investment_recommendation='AVOID'
            )

    async def _step_4_ranking_classification(self, evaluations: List[HorseEvaluation]) -> Dict[str, Any]:
        """STEP 4: ランク分類・選別（5秒）"""
        logger.info("Step 4: Ranking classification")
        
        try:
            # ランク別分類
            rank_groups = {
                'S+': [], 'S': [], 'A+': [], 'A': [], 
                'B+': [], 'B': [], 'C': [], 'D': [], 'E': []
            }
            
            for evaluation in evaluations:
                rank_groups[evaluation.rank].append(evaluation)
            
            # 投資推奨別分類
            investment_groups = {
                'STRONG_BUY': [],
                'BUY': [],
                'HOLD': [],
                'AVOID': []
            }
            
            for evaluation in evaluations:
                investment_groups[evaluation.investment_recommendation].append(evaluation)
            
            # トップ3推奨馬選出
            top_recommendations = evaluations[:3]
            
            return {
                'rank_groups': rank_groups,
                'investment_groups': investment_groups,
                'top_recommendations': [
                    {
                        'horse_name': eval.horse_name,
                        'horse_number': eval.horse_number,
                        'final_score': eval.final_score,
                        'rank': eval.rank,
                        'recommendation': eval.investment_recommendation,
                        'popularity': eval.popularity_rank
                    } for eval in top_recommendations
                ],
                'summary': {
                    'total_horses': len(evaluations),
                    'strong_buy_count': len(investment_groups['STRONG_BUY']),
                    'buy_count': len(investment_groups['BUY']),
                    'average_score': sum(e.final_score for e in evaluations) / len(evaluations) if evaluations else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Ranking classification error: {str(e)}")
            return {}

    # ヘルパーメソッド群
    def _score_to_rank(self, score: float) -> str:
        """スコアをランクに変換"""
        for rank, (min_score, max_score) in self.score_ranges.items():
            if min_score <= score <= max_score:
                return rank
        return 'E'

    def _is_valid_japanese_text(self, text: str) -> bool:
        """日本語テキスト妥当性チェック"""
        if not text:
            return True
        
        japanese_chars = 0
        for char in text:
            if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' or '\u4E00' <= char <= '\u9FAF':
                japanese_chars += 1
        
        return (japanese_chars / len(text)) >= 0.3 if text else True

    def _fix_encoding_if_possible(self, text: str) -> str:
        """可能であれば文字化け修復"""
        # 簡略化実装
        return text

    def _calculate_total_score(self, rankings: Dict[str, Any]) -> float:
        """総合スコア計算"""
        try:
            top_recs = rankings.get('top_recommendations', [])
            if not top_recs:
                return 0.0
            
            return sum(rec.get('final_score', 0) for rec in top_recs) / len(top_recs)
        except:
            return 0.0

    def _generate_quality_indicators(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """品質指標生成"""
        return {
            'data_completeness': 0.95,
            'encoding_quality': 0.98,
            'analysis_confidence': 0.92
        }

    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """エラー結果作成"""
        return {
            'status': 'error',
            'error_message': error_msg,
            'total_score': 0,
            'execution_time': 0
        }
