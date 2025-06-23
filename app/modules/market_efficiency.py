import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MarketAnalysis:
    """市場分析データクラス"""
    horse_name: str
    current_odds: float
    fair_value_odds: float
    value_gap: float
    market_sentiment: str
    betting_volume: float
    odds_trend: str
    value_rating: str

class MarketEfficiencyAnalysis:
    """市場効率性分析システム v3.1【2%重み・新機能】"""
    
    def __init__(self):
        self.max_analysis_time = 15  # 秒
        self.weight_in_system = 0.02  # システム全体の2%重み
        
        # 市場効率性分析の重み配分
        self.analysis_weights = {
            'odds_value_gap': 0.40,       # オッズと実力の乖離
            'betting_patterns': 0.25,     # 投票パターン
            'market_sentiment': 0.20,     # 市場センチメント
            'odds_movement': 0.15         # オッズ変動
        }
        
        # 価値判定基準
        self.value_thresholds = {
            'excellent_value': 1.5,    # 1.5倍以上の価値
            'good_value': 1.2,         # 1.2倍以上の価値
            'fair_value': 0.8,         # 適正価値範囲
            'overvalued': 0.6          # 過大評価
        }

    async def analyze(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """市場効率性分析実行（15秒・2%重み）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting market efficiency analysis v3.1")
        
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return self._create_error_result("No horses data")
            
            # 市場データ収集
            market_data = await self._collect_market_data(horses, race_data)
            
            # 各馬の市場効率性分析
            market_analyses = await self._analyze_all_horses_market(horses, market_data, race_data)
            
            # 割安・割高馬の特定
            value_opportunities = self._identify_value_opportunities(market_analyses)
            overvalued_risks = self._identify_overvalued_risks(market_analyses)
            
            # 市場センチメント分析
            market_sentiment = self._analyze_market_sentiment(market_analyses, market_data)
            
            # 投票パターン分析
            betting_patterns = self._analyze_betting_patterns(market_data)
            
            # 総合市場効率スコア
            overall_score = self._calculate_overall_market_score(market_analyses)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Market efficiency analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'market_efficiency_score': overall_score,
                'market_analyses': market_analyses,
                'value_opportunities': value_opportunities,
                'overvalued_risks': overvalued_risks,
                'market_sentiment': market_sentiment,
                'betting_patterns': betting_patterns,
                'market_summary': self._create_market_summary(
                    market_analyses, value_opportunities, overvalued_risks
                )
            }
            
        except Exception as e:
            logger.error(f"Market efficiency analysis error: {str(e)}")
            return self._create_error_result(str(e))

    async def _collect_market_data(self, horses: List[Dict], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """市場データ収集"""
        try:
            # 実際の実装では外部APIから取得
            # ここでは模擬データを使用
            
            market_data = {
                'total_betting_pool': 50000000,  # 5000万円
                'odds_last_update': datetime.now().isoformat(),
                'betting_trend': 'stable',
                'favorite_support': 'strong',
                'dark_horse_money': 'moderate',
                'horse_odds_data': {}
            }
            
            # 各馬のオッズデータ
            for horse in horses:
                horse_name = horse.get('horse_name', '')
                popularity = int(horse.get('popularity', 10))
                
                # 模擬オッズデータ
                odds_data = {
                    'current_odds': float(horse.get('odds', popularity * 2.0)),
                    'opening_odds': popularity * 2.5,
                    'odds_movement': 'stable',
                    'betting_volume': max(1000, 10000 - popularity * 500),
                    'support_rate': max(0.01, 0.3 - popularity * 0.02)
                }
                
                market_data['horse_odds_data'][horse_name] = odds_data
            
            return market_data
            
        except Exception as e:
            logger.error(f"Market data collection error: {str(e)}")
            return {}

    async def _analyze_all_horses_market(self, horses: List[Dict], market_data: Dict[str, Any], 
                                       race_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """全馬市場分析"""
        market_analyses = []
        
        for horse in horses:
            try:
                analysis = await self._analyze_single_horse_market(horse, market_data, race_data)
                if analysis:
                    market_analyses.append(analysis)
            except Exception as e:
                logger.error(f"Single horse market analysis error: {str(e)}")
                continue
        
        return market_analyses

    async def _analyze_single_horse_market(self, horse: Dict[str, Any], market_data: Dict[str, Any], 
                                         race_data: Dict[str, Any]) -> Dict[str, Any]:
        """単一馬市場分析"""
        try:
            horse_name = horse.get('horse_name', '')
            popularity = int(horse.get('popularity', 10))
            
            # 市場データ取得
            horse_market_data = market_data.get('horse_odds_data', {}).get(horse_name, {})
            current_odds = horse_market_data.get('current_odds', popularity * 2.0)
            
            # フェアバリュー計算
            fair_value_odds = await self._calculate_fair_value_odds(horse, race_data)
            
            # 価値ギャップ分析
            value_gap_analysis = self._analyze_value_gap(current_odds, fair_value_odds)
            
            # オッズ変動分析
            odds_movement_analysis = self._analyze_odds_movement(horse_market_data)
            
            # 投票パターン分析
            betting_pattern_analysis = self._analyze_horse_betting_pattern(horse_market_data, market_data)
            
            # 市場センチメント評価
            sentiment_analysis = self._evaluate_horse_sentiment(horse, horse_market_data, popularity)
            
            # 総合市場スコア
            market_score = self._calculate_horse_market_score(
                value_gap_analysis, odds_movement_analysis, betting_pattern_analysis, sentiment_analysis
            )
            
            return {
                'horse_name': horse_name,
                'popularity': popularity,
                'current_odds': current_odds,
                'fair_value_odds': fair_value_odds,
                'value_gap_analysis': value_gap_analysis,
                'odds_movement_analysis': odds_movement_analysis,
                'betting_pattern_analysis': betting_pattern_analysis,
                'sentiment_analysis': sentiment_analysis,
                'market_score': market_score,
                'market_rating': self._score_to_rating(market_score),
                'investment_recommendation': self._generate_market_recommendation(
                    value_gap_analysis, market_score, current_odds
                )
            }
            
        except Exception as e:
            logger.error(f"Single horse market analysis error: {str(e)}")
            return None

    async def _calculate_fair_value_odds(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> float:
        """フェアバリューオッズ計算"""
        try:
            # 実力ベースの理論勝率推定
            theoretical_win_rate = await self._estimate_theoretical_win_rate(horse, race_data)
            
            # フェアバリューオッズ = 1 / 勝率
            fair_value_odds = 1.0 / max(0.01, theoretical_win_rate)
            
            return fair_value_odds
            
        except Exception as e:
            logger.error(f"Fair value odds calculation error: {str(e)}")
            return 10.0  # デフォルト値

    async def _estimate_theoretical_win_rate(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> float:
        """理論勝率推定"""
        try:
            # 簡略化した勝率推定
            popularity = int(horse.get('popularity', 10))
            horse_count = len(race_data.get('horses', []))
            
            # 人気を基にした基本勝率
            base_win_rate = max(0.01, 0.5 - (popularity - 1) * 0.03)
            
            # 出走頭数による調整
            field_adjustment = min(1.2, 18 / max(8, horse_count))
            
            theoretical_win_rate = base_win_rate * field_adjustment
            
            return min(0.8, max(0.01, theoretical_win_rate))
            
        except Exception as e:
            logger.error(f"Theoretical win rate estimation error: {str(e)}")
            return 0.1  # デフォルト10%

    def _analyze_value_gap(self, current_odds: float, fair_value_odds: float) -> Dict[str, Any]:
        """価値ギャップ分析"""
        try:
            # 価値比率計算
            value_ratio = current_odds / fair_value_odds
            
            # 価値ギャップ
            value_gap = current_odds - fair_value_odds
            
            # 価値判定
            if value_ratio >= self.value_thresholds['excellent_value']:
                value_assessment = 'excellent_value'
            elif value_ratio >= self.value_thresholds['good_value']:
                value_assessment = 'good_value'
            elif value_ratio >= self.value_thresholds['fair_value']:
                value_assessment = 'fair_value'
            else:
                value_assessment = 'overvalued'
            
            # 価値スコア計算
            value_score = min(100, max(0, (value_ratio - 0.5) * 50))
            
            return {
                'value_ratio': value_ratio,
                'value_gap': value_gap,
                'value_assessment': value_assessment,
                'value_score': value_score,
                'investment_appeal': value_ratio >= 1.2
            }
            
        except Exception as e:
            logger.error(f"Value gap analysis error: {str(e)}")
            return {'value_score': 50.0, 'value_assessment': 'unknown'}

    def _analyze_odds_movement(self, horse_market_data: Dict[str, Any]) -> Dict[str, Any]:
        """オッズ変動分析"""
        try:
            current_odds = horse_market_data.get('current_odds', 10.0)
            opening_odds = horse_market_data.get('opening_odds', 10.0)
            
            # オッズ変動率
            if opening_odds > 0:
                odds_change_rate = (current_odds - opening_odds) / opening_odds
            else:
                odds_change_rate = 0.0
            
            # 変動方向
            if odds_change_rate > 0.05:
                movement_direction = 'drifting'  # 人気薄
            elif odds_change_rate < -0.05:
                movement_direction = 'shortening'  # 人気上昇
            else:
                movement_direction = 'stable'
            
            # 変動スコア
            movement_score = 50.0
            if movement_direction == 'shortening':
                movement_score += min(25, abs(odds_change_rate) * 100)
            elif movement_direction == 'drifting':
                movement_score -= min(25, abs(odds_change_rate) * 50)
            
            return {
                'opening_odds': opening_odds,
                'current_odds': current_odds,
                'odds_change_rate': odds_change_rate,
                'movement_direction': movement_direction,
                'movement_score': movement_score,
                'market_confidence': 'increasing' if movement_direction == 'shortening' else 
                                   'decreasing' if movement_direction == 'drifting' else 'stable'
            }
            
        except Exception as e:
            logger.error(f"Odds movement analysis error: {str(e)}")
            return {'movement_score': 50.0, 'movement_direction': 'stable'}

    def _analyze_horse_betting_pattern(self, horse_market_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """馬別投票パターン分析"""
        try:
            betting_volume = horse_market_data.get('betting_volume', 5000)
            support_rate = horse_market_data.get('support_rate', 0.1)
            total_pool = market_data.get('total_betting_pool', 50000000)
            
            # 投票集中度
            volume_share = betting_volume / total_pool
            
            # パターン分類
            if support_rate > 0.2:
                pattern_type = 'heavy_support'
            elif support_rate > 0.1:
                pattern_type = 'moderate_support'
            elif support_rate > 0.05:
                pattern_type = 'light_support'
            else:
                pattern_type = 'minimal_support'
            
            # パターンスコア
            pattern_score = min(100, support_rate * 300)
            
            return {
                'betting_volume': betting_volume,
                'support_rate': support_rate,
                'volume_share': volume_share,
                'pattern_type': pattern_type,
                'pattern_score': pattern_score,
                'public_confidence': self._assess_public_confidence(pattern_type, support_rate)
            }
            
        except Exception as e:
            logger.error(f"Horse betting pattern analysis error: {str(e)}")
            return {'pattern_score': 50.0, 'pattern_type': 'moderate_support'}

    def _calculate_horse_market_score(self, value_gap: Dict, odds_movement: Dict, 
                                    betting_pattern: Dict, sentiment: Dict) -> float:
        """馬の市場スコア計算"""
        try:
            value_score = value_gap.get('value_score', 50.0)
            movement_score = odds_movement.get('movement_score', 50.0)
            pattern_score = betting_pattern.get('pattern_score', 50.0)
            sentiment_score = sentiment.get('sentiment_score', 50.0)
            
            # 重み付き計算
            total_score = (
                value_score * self.analysis_weights['odds_value_gap'] +
                pattern_score * self.analysis_weights['betting_patterns'] +
                sentiment_score * self.analysis_weights['market_sentiment'] +
                movement_score * self.analysis_weights['odds_movement']
            )
            
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"Horse market score calculation error: {str(e)}")
            return 50.0

    def _identify_value_opportunities(self, market_analyses: List[Dict]) -> List[Dict]:
        """割安機会特定"""
        try:
            value_opportunities = []
            
            for analysis in market_analyses:
                value_gap = analysis.get('value_gap_analysis', {})
                market_score = analysis.get('market_score', 0)
                
                if (value_gap.get('value_assessment') in ['excellent_value', 'good_value'] and
                    market_score >= 60.0):
                    
                    opportunity = {
                        'horse_name': analysis.get('horse_name', ''),
                        'current_odds': analysis.get('current_odds', 0),
                        'fair_value_odds': analysis.get('fair_value_odds', 0),
                        'value_ratio': value_gap.get('value_ratio', 1.0),
                        'market_score': market_score,
                        'opportunity_type': value_gap.get('value_assessment', ''),
                        'confidence_level': self._calculate_opportunity_confidence(analysis)
                    }
                    value_opportunities.append(opportunity)
            
            # 価値比率でソート
            value_opportunities.sort(key=lambda x: x['value_ratio'], reverse=True)
            
            return value_opportunities[:5]  # 上位5頭まで
            
        except Exception as e:
            logger.error(f"Value opportunities identification error: {str(e)}")
            return []

    def _identify_overvalued_risks(self, market_analyses: List[Dict]) -> List[Dict]:
        """割高リスク特定"""
        try:
            overvalued_risks = []
            
            for analysis in market_analyses:
                value_gap = analysis.get('value_gap_analysis', {})
                
                if value_gap.get('value_assessment') == 'overvalued':
                    risk = {
                        'horse_name': analysis.get('horse_name', ''),
                        'current_odds': analysis.get('current_odds', 0),
                        'fair_value_odds': analysis.get('fair_value_odds', 0),
                        'value_ratio': value_gap.get('value_ratio', 1.0),
                        'risk_level': self._assess_overvaluation_risk(value_gap),
                        'avoidance_reason': '市場価値に対して過大評価'
                    }
                    overvalued_risks.append(risk)
            
            return overvalued_risks
            
        except Exception as e:
            logger.error(f"Overvalued risks identification error: {str(e)}")
            return []

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
            'market_efficiency_score': 0,
            'execution_time': 0
        }

    # ... その他のヘルパーメソッドは実装省略（実際の開発時に詳細実装）
    def _evaluate_horse_sentiment(self, horse: Dict, market_data: Dict, popularity: int) -> Dict[str, Any]:
        """馬別センチメント評価"""
        return {'sentiment_score': 50.0, 'sentiment': 'neutral'}

    def _analyze_market_sentiment(self, analyses: List[Dict], market_data: Dict) -> Dict[str, Any]:
        """市場センチメント分析"""
        return {'overall_sentiment': 'neutral', 'confidence': 'medium'}

    def _analyze_betting_patterns(self, market_data: Dict) -> Dict[str, Any]:
        """投票パターン分析"""
        return {'pattern': 'normal', 'concentration': 'moderate'}

    # ... その他も同様に簡略化実装
