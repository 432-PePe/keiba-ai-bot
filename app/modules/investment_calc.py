import logging
import asyncio
import math
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class InvestmentRecommendation:
    """投資推奨データクラス"""
    horse_name: str
    bet_type: str  # 'win', 'place', 'exacta', 'trifecta'
    recommended_amount: int
    expected_return: float
    confidence_level: float
    risk_level: str
    kelly_fraction: float

class InvestmentCalculator:
    """最適投資額算出システム v3.1【ケリー基準+リスク分散強化】"""
    
    def __init__(self):
        self.daily_limit = 20000  # 1日の投資上限（円）
        self.max_single_bet = 5000  # 単一賭けの上限（円）
        self.min_bet_amount = 100  # 最小賭け金額（円）
        self.kelly_modifier = 0.25  # ケリー基準の保守的調整（25%）
        
        # リスク管理パラメータ
        self.risk_levels = {
            'conservative': {'max_bet_ratio': 0.15, 'min_confidence': 0.7},
            'moderate': {'max_bet_ratio': 0.25, 'min_confidence': 0.6},
            'aggressive': {'max_bet_ratio': 0.4, 'min_confidence': 0.5}
        }
        
        # 馬券種別設定
        self.bet_types = {
            'win': {'min_odds': 1.1, 'max_odds': 50.0, 'base_confidence': 0.8},
            'place': {'min_odds': 1.1, 'max_odds': 10.0, 'base_confidence': 0.9},
            'exacta': {'min_odds': 3.0, 'max_odds': 500.0, 'base_confidence': 0.6},
            'trifecta': {'min_odds': 10.0, 'max_odds': 5000.0, 'base_confidence': 0.4}
        }

    async def calculate(self, evaluation_data: Dict[str, Any], daily_limit: int = None) -> Dict[str, Any]:
        """最適投資額算出（25秒以内）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting investment calculation with Kelly criterion")
        
        try:
            if daily_limit:
                self.daily_limit = daily_limit
            
            # 評価データから投資候補抽出
            investment_candidates = self._extract_investment_candidates(evaluation_data)
            
            if not investment_candidates:
                return self._create_no_investment_result("No suitable investment candidates")
            
            # 各候補の期待値・リスク計算
            candidate_analysis = await self._analyze_candidates(investment_candidates)
            
            # ケリー基準による最適投資額計算
            kelly_recommendations = self._calculate_kelly_recommendations(candidate_analysis)
            
            # リスク分散調整
            diversified_strategy = self._apply_risk_diversification(kelly_recommendations)
            
            # 最終投資プラン作成
            final_strategy = self._create_final_investment_plan(diversified_strategy)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Investment calculation completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'daily_limit': self.daily_limit,
                'total_recommended_amount': sum(rec.recommended_amount for rec in final_strategy),
                'investment_recommendations': [
                    {
                        'horse_name': rec.horse_name,
                        'bet_type': rec.bet_type,
                        'recommended_amount': rec.recommended_amount,
                        'expected_return': rec.expected_return,
                        'confidence_level': rec.confidence_level,
                        'risk_level': rec.risk_level,
                        'kelly_fraction': rec.kelly_fraction
                    } for rec in final_strategy
                ],
                'risk_analysis': self._generate_risk_analysis(final_strategy),
                'portfolio_summary': self._generate_portfolio_summary(final_strategy)
            }
            
        except Exception as e:
            logger.error(f"Investment calculation error: {str(e)}")
            return self._create_error_result(str(e))

    def _extract_investment_candidates(self, evaluation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """投資候補抽出"""
        candidates = []
        
        try:
            # 基本分析からの推奨馬
            final_rankings = evaluation_data.get('final_rankings', {})
            top_recommendations = final_rankings.get('top_recommendations', [])
            
            for horse in top_recommendations:
                if horse.get('final_score', 0) >= 70:  # 70点以上のみ
                    candidates.append({
                        'horse_name': horse.get('horse_name', ''),
                        'horse_number': horse.get('horse_number', 0),
                        'final_score': horse.get('final_score', 0),
                        'rank': horse.get('rank', 'C'),
                        'popularity': horse.get('popularity', 99),
                        'recommendation': horse.get('recommendation', 'AVOID'),
                        'source': 'basic_analysis'
                    })
            
            # 穴馬発掘からの追加候補
            dark_horse_results = evaluation_data.get('dark_horse_analysis', {})
            dark_horses = dark_horse_results.get('recommended_horses', [])
            
            for horse in dark_horses:
                if horse.get('dark_horse_score', 0) >= 75:  # 穴馬スコア75以上
                    candidates.append({
                        'horse_name': horse.get('horse_name', ''),
                        'horse_number': horse.get('horse_number', 0),
                        'final_score': horse.get('dark_horse_score', 0),
                        'rank': 'DARK_HORSE',
                        'popularity': horse.get('popularity', 99),
                        'recommendation': 'DARK_HORSE',
                        'source': 'dark_horse_analysis'
                    })
            
            # 重複除去
            unique_candidates = self._remove_duplicate_candidates(candidates)
            
            logger.info(f"Extracted {len(unique_candidates)} investment candidates")
            return unique_candidates
            
        except Exception as e:
            logger.error(f"Candidate extraction error: {str(e)}")
            return []

    async def _analyze_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """候補分析"""
        analyzed_candidates = []
        
        for candidate in candidates:
            try:
                analysis = await self._analyze_single_candidate(candidate)
                if analysis:
                    analyzed_candidates.append(analysis)
            except Exception as e:
                logger.error(f"Candidate analysis error: {str(e)}")
                continue
        
        return analyzed_candidates

    async def _analyze_single_candidate(self, candidate: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """単一候補分析"""
        try:
            horse_name = candidate.get('horse_name', '')
            final_score = candidate.get('final_score', 0)
            popularity = candidate.get('popularity', 99)
            source = candidate.get('source', 'unknown')
            
            # オッズ推定（実際は最新オッズを取得）
            estimated_odds = self._estimate_odds_from_popularity(popularity)
            
            # 勝率推定
            estimated_win_prob = self._estimate_win_probability(final_score, source)
            
            # 連対率推定
            estimated_place_prob = self._estimate_place_probability(final_score, source)
            
            # 期待値計算
            win_expected_value = self._calculate_expected_value(estimated_win_prob, estimated_odds)
            place_expected_value = self._calculate_expected_value(estimated_place_prob, estimated_odds * 0.4)  # 複勝は約40%のオッズ
            
            # 信頼度計算
            confidence_level = self._calculate_confidence_level(final_score, source, popularity)
            
            return {
                'candidate': candidate,
                'estimated_odds': estimated_odds,
                'estimated_win_prob': estimated_win_prob,
                'estimated_place_prob': estimated_place_prob,
                'win_expected_value': win_expected_value,
                'place_expected_value': place_expected_value,
                'confidence_level': confidence_level,
                'risk_assessment': self._assess_risk_level(confidence_level, estimated_odds)
            }
            
        except Exception as e:
            logger.error(f"Single candidate analysis error: {str(e)}")
            return None

    def _calculate_kelly_recommendations(self, candidates: List[Dict[str, Any]]) -> List[InvestmentRecommendation]:
        """ケリー基準による投資推奨計算"""
        recommendations = []
        
        for candidate_data in candidates:
            try:
                candidate = candidate_data['candidate']
                horse_name = candidate['horse_name']
                
                # 単勝のケリー計算
                win_kelly = self._calculate_kelly_fraction(
                    candidate_data['estimated_win_prob'],
                    candidate_data['estimated_odds']
                )
                
                if win_kelly > 0.01:  # 1%以上の場合のみ投資検討
                    win_amount = self._kelly_to_amount(win_kelly, 'win')
                    
                    recommendations.append(InvestmentRecommendation(
                        horse_name=horse_name,
                        bet_type='win',
                        recommended_amount=win_amount,
                        expected_return=candidate_data['win_expected_value'],
                        confidence_level=candidate_data['confidence_level'],
                        risk_level=candidate_data['risk_assessment'],
                        kelly_fraction=win_kelly
                    ))
                
                # 複勝のケリー計算
                place_kelly = self._calculate_kelly_fraction(
                    candidate_data['estimated_place_prob'],
                    candidate_data['estimated_odds'] * 0.4
                )
                
                if place_kelly > 0.01:
                    place_amount = self._kelly_to_amount(place_kelly, 'place')
                    
                    recommendations.append(InvestmentRecommendation(
                        horse_name=horse_name,
                        bet_type='place',
                        recommended_amount=place_amount,
                        expected_return=candidate_data['place_expected_value'],
                        confidence_level=candidate_data['confidence_level'],
                        risk_level=candidate_data['risk_assessment'],
                        kelly_fraction=place_kelly
                    ))
                
                # 馬連・3連複の検討（上位候補のみ）
                if candidate_data['confidence_level'] >= 0.8:
                    exotic_recommendations = self._calculate_exotic_bets(candidate_data)
                    recommendations.extend(exotic_recommendations)
                    
            except Exception as e:
                logger.error(f"Kelly calculation error: {str(e)}")
                continue
        
        return recommendations

    def _calculate_kelly_fraction(self, win_probability: float, odds: float) -> float:
        """ケリー基準の計算"""
        try:
            if odds <= 1.0 or win_probability <= 0:
                return 0.0
            
            # ケリー公式: f = (bp - q) / b
            # b = オッズ-1, p = 勝率, q = 負け率
            b = odds - 1
            p = win_probability
            q = 1 - p
            
            kelly_fraction = (b * p - q) / b
            
            # 保守的調整（25%に制限）
            adjusted_kelly = max(0, kelly_fraction * self.kelly_modifier)
            
            # 最大10%に制限
            return min(0.1, adjusted_kelly)
            
        except Exception as e:
            logger.error(f"Kelly fraction calculation error: {str(e)}")
            return 0.0

    def _kelly_to_amount(self, kelly_fraction: float, bet_type: str) -> int:
        """ケリー比率を金額に変換"""
        try:
            # 利用可能資金に対する比率
            available_funds = self.daily_limit
            raw_amount = available_funds * kelly_fraction
            
            # 馬券種別による調整
            if bet_type == 'place':
                raw_amount *= 1.2  # 複勝は安全性が高いため増額
            elif bet_type in ['exacta', 'trifecta']:
                raw_amount *= 0.6  # 複雑な馬券は減額
            
            # 100円単位に調整
            amount = int(raw_amount // 100) * 100
            
            # 制限チェック
            amount = max(self.min_bet_amount, amount)
            amount = min(self.max_single_bet, amount)
            
            return amount
            
        except Exception as e:
            logger.error(f"Amount conversion error: {str(e)}")
            return self.min_bet_amount

    def _apply_risk_diversification(self, recommendations: List[InvestmentRecommendation]) -> List[InvestmentRecommendation]:
        """リスク分散調整"""
        try:
            if not recommendations:
                return recommendations
            
            # 総投資額計算
            total_amount = sum(rec.recommended_amount for rec in recommendations)
            
            # 上限超過の場合は比例縮小
            if total_amount > self.daily_limit:
                scale_factor = self.daily_limit / total_amount
                
                for rec in recommendations:
                    new_amount = int(rec.recommended_amount * scale_factor // 100) * 100
                    rec.recommended_amount = max(self.min_bet_amount, new_amount)
            
            # リスクバランス調整
            high_risk_count = sum(1 for rec in recommendations if rec.risk_level == 'high')
            
            if high_risk_count > 2:  # 高リスク投資が多すぎる場合
                # 高リスク投資を削減
                recommendations.sort(key=lambda x: x.confidence_level, reverse=True)
                filtered_recommendations = []
                
                high_risk_added = 0
                for rec in recommendations:
                    if rec.risk_level == 'high' and high_risk_added >= 2:
                        continue
                    
                    filtered_recommendations.append(rec)
                    if rec.risk_level == 'high':
                        high_risk_added += 1
                
                recommendations = filtered_recommendations
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Risk diversification error: {str(e)}")
            return recommendations

    def _create_final_investment_plan(self, recommendations: List[InvestmentRecommendation]) -> List[InvestmentRecommendation]:
        """最終投資プラン作成"""
        try:
            # 信頼度でソート
            recommendations.sort(key=lambda x: x.confidence_level, reverse=True)
            
            # 最終調整
            final_plan = []
            total_allocated = 0
            
            for rec in recommendations:
                if total_allocated + rec.recommended_amount <= self.daily_limit:
                    final_plan.append(rec)
                    total_allocated += rec.recommended_amount
                else:
                    # 残り予算で可能な金額に調整
                    remaining_budget = self.daily_limit - total_allocated
                    if remaining_budget >= self.min_bet_amount:
                        adjusted_amount = int(remaining_budget // 100) * 100
                        rec.recommended_amount = adjusted_amount
                        final_plan.append(rec)
                    break
            
            return final_plan
            
        except Exception as e:
            logger.error(f"Final plan creation error: {str(e)}")
            return recommendations

    # ヘルパーメソッド
    def _estimate_odds_from_popularity(self, popularity: int) -> float:
        """人気からオッズ推定"""
        odds_map = {1: 2.5, 2: 4.0, 3: 6.0, 4: 8.0, 5: 12.0}
        return odds_map.get(popularity, min(20.0, popularity * 2.5))

    def _estimate_win_probability(self, final_score: float, source: str) -> float:
        """勝率推定"""
        base_prob = final_score / 1000  # 100点満点を0.1に変換
        
        if source == 'dark_horse_analysis':
            base_prob *= 0.7  # 穴馬は保守的に
        
        return max(0.01, min(0.5, base_prob))

    def _estimate_place_probability(self, final_score: float, source: str) -> float:
        """連対率推定"""
        return min(0.8, self._estimate_win_probability(final_score, source) * 3)

    def _calculate_expected_value(self, win_prob: float, odds: float) -> float:
        """期待値計算"""
        return (win_prob * odds) - 1.0

    def _calculate_confidence_level(self, final_score: float, source: str, popularity: int) -> float:
        """信頼度計算"""
        base_confidence = final_score / 100
        
        # 人気による調整
        if popularity <= 3:
            popularity_bonus = 0.1
        elif popularity <= 6:
            popularity_bonus = 0.0
        else:
            popularity_bonus = -0.1
        
        return max(0.1, min(1.0, base_confidence + popularity_bonus))

    def _assess_risk_level(self, confidence: float, odds: float) -> str:
        """リスクレベル評価"""
        if confidence >= 0.8 and odds <= 5.0:
            return 'low'
        elif confidence >= 0.6 and odds <= 15.0:
            return 'medium'
        else:
            return 'high'

    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """エラー結果作成"""
        return {
            'status': 'error',
            'error_message': error_msg,
            'total_recommended_amount': 0,
            'investment_recommendations': []
        }

    def _create_no_investment_result(self, reason: str) -> Dict[str, Any]:
        """投資なし結果作成"""
        return {
            'status': 'no_investment',
            'reason': reason,
            'total_recommended_amount': 0,
            'investment_recommendations': [],
            'message': '本日は投資を見送ります。'
        }
