import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DarkHorseCandidate:
    """穴馬候補データクラス"""
    horse_name: str
    horse_number: int
    popularity: int
    estimated_odds: float
    dark_horse_score: float
    upset_factors: List[str]
    expected_value: float
    confidence_level: float
    recommendation_type: str

class DarkHorseAnalysis:
    """穴馬発掘分析システム v3.1【5%重み・価値発見特化】"""
    
    def __init__(self):
        self.max_analysis_time = 10  # 秒
        self.weight_in_system = 0.05  # システム全体の5%重み
        
        # 穴馬発掘の重み配分
        self.analysis_weights = {
            'market_inefficiency': 0.30,    # 市場非効率性
            'hidden_ability': 0.25,         # 隠れた能力
            'condition_change': 0.20,       # 条件変更適性
            'jockey_trainer_combo': 0.15,   # 騎手厩舎コンビ
            'seasonal_factor': 0.10         # 季節的要因
        }
        
        # 穴馬パターン定義
        self.upset_patterns = {
            'distance_change': {
                'short_to_long': '距離延長で開花',
                'long_to_short': '距離短縮で切れ味向上',
                'optimal_distance': '最適距離への回帰'
            },
            'surface_change': {
                'turf_to_dirt': '芝からダートで激変',
                'dirt_to_turf': 'ダートから芝で本領発揮'
            },
            'class_change': {
                'class_drop': '格下げで実力発揮',
                'maiden_break': '未勝利脱出の機運'
            },
            'layoff_return': {
                'fresh_comeback': '休み明けで気力充実',
                'equipment_change': '装具変更で変身'
            }
        }
        
        # 穴馬候補の人気圏
        self.dark_horse_popularity_range = (6, 16)  # 6-16番人気
        
        # 期待オッズ範囲
        self.target_odds_range = (8.0, 50.0)  # 8-50倍

    async def analyze(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """穴馬発掘分析実行（10秒・5%重み）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting dark horse analysis v3.1")
        
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return self._create_error_result("No horses data")
            
            # 穴馬候補フィルタリング
            dark_horse_candidates = self._filter_dark_horse_candidates(horses)
            
            if not dark_horse_candidates:
                return self._create_no_candidates_result()
            
            # 各候補の詳細分析
            analyzed_candidates = await self._analyze_all_candidates(dark_horse_candidates, race_data)
            
            # 穴馬スコアでソート
            ranked_candidates = sorted(analyzed_candidates, key=lambda x: x.get('dark_horse_score', 0), reverse=True)
            
            # 推奨穴馬選出
            recommended_horses = self._select_recommended_dark_horses(ranked_candidates)
            
            # 穴馬戦略分析
            upset_strategy = self._develop_upset_strategy(recommended_horses, race_data)
            
            # 期待値分析
            value_analysis = self._calculate_value_expectations(recommended_horses)
            
            # 総合穴馬スコア
            overall_score = self._calculate_overall_dark_horse_score(ranked_candidates)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Dark horse analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'dark_horse_score': overall_score,
                'total_candidates': len(dark_horse_candidates),
                'analyzed_candidates': analyzed_candidates,
                'ranked_candidates': ranked_candidates,
                'recommended_horses': recommended_horses,
                'upset_strategy': upset_strategy,
                'value_analysis': value_analysis,
                'dark_horse_summary': self._create_dark_horse_summary(recommended_horses)
            }
            
        except Exception as e:
            logger.error(f"Dark horse analysis error: {str(e)}")
            return self._create_error_result(str(e))

    def _filter_dark_horse_candidates(self, horses: List[Dict]) -> List[Dict]:
        """穴馬候補フィルタリング"""
        candidates = []
        
        try:
            for horse in horses:
                popularity = int(horse.get('popularity', 99))
                odds = float(horse.get('odds', 99.0))
                
                # 人気圏チェック
                if (self.dark_horse_popularity_range[0] <= popularity <= self.dark_horse_popularity_range[1] and
                    self.target_odds_range[0] <= odds <= self.target_odds_range[1]):
                    candidates.append(horse)
            
            logger.info(f"Filtered {len(candidates)} dark horse candidates from {len(horses)} horses")
            return candidates
            
        except Exception as e:
            logger.error(f"Dark horse candidate filtering error: {str(e)}")
            return []

    async def _analyze_all_candidates(self, candidates: List[Dict], race_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """全候補分析"""
        analyzed_candidates = []
        
        for candidate in candidates:
            try:
                analysis = await self._analyze_single_candidate(candidate, race_data)
                if analysis:
                    analyzed_candidates.append(analysis)
            except Exception as e:
                logger.error(f"Single candidate analysis error: {str(e)}")
                continue
        
        return analyzed_candidates

    async def _analyze_single_candidate(self, candidate: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """単一候補分析"""
        try:
            horse_name = candidate.get('horse_name', '')
            horse_number = int(candidate.get('horse_number', 0))
            popularity = int(candidate.get('popularity', 99))
            estimated_odds = float(candidate.get('odds', 99.0))
            
            # 市場非効率性分析（30%重み）
            market_inefficiency = await self._analyze_market_inefficiency(candidate, race_data)
            
            # 隠れた能力分析（25%重み）
            hidden_ability = await self._analyze_hidden_ability(candidate, race_data)
            
            # 条件変更適性分析（20%重み）
            condition_change = await self._analyze_condition_change_aptitude(candidate, race_data)
            
            # 騎手厩舎コンビ分析（15%重み）
            jockey_trainer_combo = await self._analyze_jockey_trainer_combination(candidate)
            
            # 季節的要因分析（10%重み）
            seasonal_factor = await self._analyze_seasonal_factors(candidate, race_data)
            
            # 穴馬要因特定
            upset_factors = self._identify_upset_factors(
                market_inefficiency, hidden_ability, condition_change, 
                jockey_trainer_combo, seasonal_factor
            )
            
            # 穴馬スコア計算
            dark_horse_score = self._calculate_dark_horse_score(
                market_inefficiency, hidden_ability, condition_change,
                jockey_trainer_combo, seasonal_factor
            )
            
            # 期待値計算
            expected_value = self._calculate_expected_value(dark_horse_score, estimated_odds)
            
            # 信頼度評価
            confidence_level = self._evaluate_confidence_level(
                dark_horse_score, len(upset_factors), market_inefficiency
            )
            
            # 推奨タイプ決定
            recommendation_type = self._determine_recommendation_type(
                dark_horse_score, expected_value, confidence_level
            )
            
            return {
                'horse_name': horse_name,
                'horse_number': horse_number,
                'popularity': popularity,
                'estimated_odds': estimated_odds,
                'market_inefficiency': market_inefficiency,
                'hidden_ability': hidden_ability,
                'condition_change': condition_change,
                'jockey_trainer_combo': jockey_trainer_combo,
                'seasonal_factor': seasonal_factor,
                'upset_factors': upset_factors,
                'dark_horse_score': dark_horse_score,
                'expected_value': expected_value,
                'confidence_level': confidence_level,
                'recommendation_type': recommendation_type,
                'dark_horse_rating': self._score_to_rating(dark_horse_score)
            }
            
        except Exception as e:
            logger.error(f"Single candidate analysis error: {str(e)}")
            return None

    async def _analyze_market_inefficiency(self, candidate: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """市場非効率性分析（30%重み）"""
        try:
            popularity = int(candidate.get('popularity', 99))
            estimated_odds = float(candidate.get('odds', 99.0))
            
            # 理論的な実力評価（簡略化）
            theoretical_ability = await self._estimate_theoretical_ability(candidate, race_data)
            
            # 理論オッズ計算
            theoretical_odds = self._calculate_theoretical_odds(theoretical_ability, popularity)
            
            # 市場との乖離度
            odds_gap = estimated_odds - theoretical_odds
            inefficiency_score = min(100, max(0, (odds_gap / theoretical_odds) * 100))
            
            # 人気薄要因分析
            unpopular_factors = self._analyze_unpopular_factors(candidate, race_data)
            
            return {
                'inefficiency_score': inefficiency_score,
                'theoretical_ability': theoretical_ability,
                'theoretical_odds': theoretical_odds,
                'actual_odds': estimated_odds,
                'odds_gap': odds_gap,
                'unpopular_factors': unpopular_factors,
                'market_value': 'undervalued' if odds_gap > 2.0 else 'fairly_valued' if odds_gap > -2.0 else 'overvalued'
            }
            
        except Exception as e:
            logger.error(f"Market inefficiency analysis error: {str(e)}")
            return {'inefficiency_score': 0.0, 'market_value': 'unknown'}

    async def _analyze_hidden_ability(self, candidate: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """隠れた能力分析（25%重み）"""
        try:
            # 過去成績から隠れた能力を発掘
            past_performances = await self._get_candidate_past_performances(candidate)
            
            # 好走歴分析
            good_runs = self._analyze_good_runs(past_performances)
            
            # 成長性分析
            improvement_trend = self._analyze_improvement_trend(past_performances)
            
            # 未発揮能力分析
            untapped_potential = self._analyze_untapped_potential(past_performances, race_data)
            
            # クラス適性分析
            class_potential = self._analyze_class_potential(past_performances, race_data)
            
            # 隠れた能力スコア
            hidden_ability_score = (
                good_runs.get('score', 0) * 0.3 +
                improvement_trend.get('score', 0) * 0.25 +
                untapped_potential.get('score', 0) * 0.25 +
                class_potential.get('score', 0) * 0.2
            )
            
            return {
                'hidden_ability_score': hidden_ability_score,
                'good_runs': good_runs,
                'improvement_trend': improvement_trend,
                'untapped_potential': untapped_potential,
                'class_potential': class_potential,
                'ability_assessment': self._assess_hidden_ability(hidden_ability_score)
            }
            
        except Exception as e:
            logger.error(f"Hidden ability analysis error: {str(e)}")
            return {'hidden_ability_score': 0.0, 'ability_assessment': 'unknown'}

    async def _analyze_condition_change_aptitude(self, candidate: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """条件変更適性分析（20%重み）"""
        try:
            # 距離変更適性
            distance_change = self._analyze_distance_change_aptitude(candidate, race_data)
            
            # 馬場変更適性
            surface_change = self._analyze_surface_change_aptitude(candidate, race_data)
            
            # クラス変更適性
            class_change = self._analyze_class_change_aptitude(candidate, race_data)
            
            # 競馬場変更適性
            track_change = self._analyze_track_change_aptitude(candidate, race_data)
            
            # 条件変更スコア
            condition_change_score = (
                distance_change.get('score', 0) * 0.4 +
                surface_change.get('score', 0) * 0.3 +
                class_change.get('score', 0) * 0.2 +
                track_change.get('score', 0) * 0.1
            )
            
            return {
                'condition_change_score': condition_change_score,
                'distance_change': distance_change,
                'surface_change': surface_change,
                'class_change': class_change,
                'track_change': track_change,
                'change_benefits': self._identify_change_benefits(
                    distance_change, surface_change, class_change
                )
            }
            
        except Exception as e:
            logger.error(f"Condition change aptitude analysis error: {str(e)}")
            return {'condition_change_score': 0.0, 'change_benefits': []}

    def _calculate_dark_horse_score(self, market_inefficiency: Dict, hidden_ability: Dict, 
                                  condition_change: Dict, jockey_trainer_combo: Dict, 
                                  seasonal_factor: Dict) -> float:
        """穴馬スコア計算"""
        try:
            market_score = market_inefficiency.get('inefficiency_score', 0.0)
            ability_score = hidden_ability.get('hidden_ability_score', 0.0)
            condition_score = condition_change.get('condition_change_score', 0.0)
            combo_score = jockey_trainer_combo.get('combo_score', 0.0)
            seasonal_score = seasonal_factor.get('seasonal_score', 0.0)
            
            # 重み付き計算
            total_score = (
                market_score * self.analysis_weights['market_inefficiency'] +
                ability_score * self.analysis_weights['hidden_ability'] +
                condition_score * self.analysis_weights['condition_change'] +
                combo_score * self.analysis_weights['jockey_trainer_combo'] +
                seasonal_score * self.analysis_weights['seasonal_factor']
            )
            
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"Dark horse score calculation error: {str(e)}")
            return 0.0

    def _calculate_expected_value(self, dark_horse_score: float, odds: float) -> float:
        """期待値計算"""
        try:
            # 穴馬スコアから勝率推定
            estimated_win_probability = min(0.3, dark_horse_score / 500)  # 最大30%
            
            # 期待値 = (勝率 × オッズ) - 1
            expected_value = (estimated_win_probability * odds) - 1.0
            
            return expected_value
            
        except Exception as e:
            logger.error(f"Expected value calculation error: {str(e)}")
            return -1.0

    def _select_recommended_dark_horses(self, ranked_candidates: List[Dict]) -> List[Dict]:
        """推奨穴馬選出"""
        try:
            recommended = []
            
            for candidate in ranked_candidates:
                dark_horse_score = candidate.get('dark_horse_score', 0)
                expected_value = candidate.get('expected_value', -1)
                confidence_level = candidate.get('confidence_level', 0)
                
                # 推奨基準
                if (dark_horse_score >= 60.0 and 
                    expected_value >= 0.5 and 
                    confidence_level >= 0.6):
                    recommended.append(candidate)
                
                # 最大3頭まで
                if len(recommended) >= 3:
                    break
            
            return recommended
            
        except Exception as e:
            logger.error(f"Recommended dark horses selection error: {str(e)}")
            return []

    def _develop_upset_strategy(self, recommended_horses: List[Dict], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """穴馬戦略策定"""
        try:
            if not recommended_horses:
                return {'strategy': 'no_upset_opportunity', 'recommendations': []}
            
            strategies = []
            
            for horse in recommended_horses:
                horse_name = horse.get('horse_name', '')
                dark_horse_score = horse.get('dark_horse_score', 0)
                expected_value = horse.get('expected_value', 0)
                upset_factors = horse.get('upset_factors', [])
                
                if dark_horse_score >= 75:
                    strategy_type = 'aggressive_bet'
                elif dark_horse_score >= 60:
                    strategy_type = 'moderate_bet'
                else:
                    strategy_type = 'small_bet'
                
                strategies.append({
                    'horse_name': horse_name,
                    'strategy_type': strategy_type,
                    'confidence': dark_horse_score,
                    'expected_value': expected_value,
                    'key_factors': upset_factors[:3],
                    'bet_recommendation': self._generate_bet_recommendation(horse)
                })
            
            return {
                'strategy': 'multi_horse_upset' if len(strategies) > 1 else 'single_horse_focus',
                'total_candidates': len(recommended_horses),
                'strategies': strategies,
                'overall_assessment': self._assess_overall_upset_potential(recommended_horses)
            }
            
        except Exception as e:
            logger.error(f"Upset strategy development error: {str(e)}")
            return {'strategy': 'error', 'recommendations': []}

    # ヘルパーメソッド
    def _score_to_rating(self, score: float) -> str:
        """スコアを評価に変換"""
        if score >= 80:
            return 'excellent'
        elif score >= 65:
            return 'good'
        elif score >= 50:
            return 'average'
        elif score >= 35:
            return 'poor'
        else:
            return 'very_poor'

    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """エラー結果作成"""
        return {
            'status': 'error',
            'error_message': error_msg,
            'dark_horse_score': 0,
            'recommended_horses': [],
            'execution_time': 0
        }

    def _create_no_candidates_result(self) -> Dict[str, Any]:
        """候補なし結果作成"""
        return {
            'status': 'no_candidates',
            'message': '穴馬候補が見つかりませんでした',
            'dark_horse_score': 0,
            'recommended_horses': [],
            'total_candidates': 0
        }

    # ... その他のヘルパーメソッドは実装省略（実際の開発時に詳細実装）
    async def _estimate_theoretical_ability(self, candidate: Dict, race_data: Dict) -> float:
        """理論実力推定"""
        return 65.0  # 簡略化

    def _calculate_theoretical_odds(self, ability: float, popularity: int) -> float:
        """理論オッズ計算"""
        return max(3.0, popularity * 1.5)  # 簡略化

    async def _get_candidate_past_performances(self, candidate: Dict) -> List[Dict]:
        """候補馬過去成績取得"""
        return []  # 簡略化

    def _analyze_good_runs(self, performances: List[Dict]) -> Dict[str, Any]:
        """好走歴分析"""
        return {'score': 50.0, 'good_runs_count': 0}  # 簡略化

    # ... その他も同様に簡略化実装
