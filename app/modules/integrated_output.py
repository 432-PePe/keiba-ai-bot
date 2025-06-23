import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class IntegratedOutput:
    """統合評価出力システム v3.1【15要素統合】"""
    
    def __init__(self):
        # モジュール重み設定（v3.1最適化）
        self.module_weights = {
            'jockey_trainer': 0.22,      # 騎手厩舎相性分析
            'basic_analysis': 0.20,      # 基本分析
            'ability_analysis': 0.18,    # 実戦能力分析
            'bloodline': 0.15,           # 血統適性分析
            'performance_rate': 0.15,    # 連帯率実績分析
            'dark_horse': 0.05,          # 穴馬発掘分析
            'pre_race_info': 0.03,       # 直前情報分析
            'market_efficiency': 0.02    # 市場効率性分析
        }

    async def generate(self, race_data: Dict[str, Any], 
                      analysis_results: List[Any], 
                      integration_results: Dict[str, Any]) -> Dict[str, Any]:
        """統合評価生成（35秒以内）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting integrated evaluation generation")
        
        try:
            # 全分析結果の統合
            integrated_scores = self._integrate_all_analysis(analysis_results)
            
            # 重み付き総合評価計算
            weighted_evaluation = self._calculate_weighted_evaluation(integrated_scores)
            
            # 最終推奨馬決定
            final_recommendations = self._determine_final_recommendations(weighted_evaluation)
            
            # 詳細分析レポート生成
            detailed_report = self._generate_detailed_report(
                race_data, analysis_results, integration_results, final_recommendations
            )
            
            # 品質スコア計算
            quality_score = self._calculate_quality_score(analysis_results)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Integrated evaluation completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'recommendations': final_recommendations,
                'integrated_scores': integrated_scores,
                'weighted_evaluation': weighted_evaluation,
                'detailed_report': detailed_report,
                'quality_score': quality_score,
                'confidence_level': self._calculate_overall_confidence(analysis_results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Integrated output generation error: {str(e)}")
            return self._create_error_result(str(e))

    def _integrate_all_analysis(self, analysis_results: List[Any]) -> Dict[str, Any]:
        """全分析結果統合"""
        integrated = {}
        
        try:
            for result in analysis_results:
                module_name = result.module_name
                weight = result.weight
                score = result.score
                details = result.details
                
                integrated[module_name] = {
                    'weight': weight,
                    'score': score,
                    'details': details,
                    'status': result.status,
                    'execution_time': result.execution_time
                }
            
            return integrated
            
        except Exception as e:
            logger.error(f"Analysis integration error: {str(e)}")
            return {}

    def _calculate_weighted_evaluation(self, integrated_scores: Dict[str, Any]) -> Dict[str, Any]:
        """重み付き総合評価計算"""
        try:
            total_weighted_score = 0
            total_weight = 0
            module_contributions = {}
            
            for module_name, module_data in integrated_scores.items():
                weight = module_data.get('weight', 0)
                score = module_data.get('score', 0)
                
                weighted_contribution = weight * score
                total_weighted_score += weighted_contribution
                total_weight += weight
                
                module_contributions[module_name] = {
                    'weight': weight,
                    'score': score,
                    'contribution': weighted_contribution,
                    'percentage': (weight * 100) if total_weight > 0 else 0
                }
            
            # 正規化
            final_score = total_weighted_score / total_weight if total_weight > 0 else 0
            
            return {
                'final_score': final_score,
                'total_weight': total_weight,
                'module_contributions': module_contributions,
                'evaluation_grade': self._score_to_grade(final_score)
            }
            
        except Exception as e:
            logger.error(f"Weighted evaluation calculation error: {str(e)}")
            return {'final_score': 0, 'evaluation_grade': 'F'}

    def _determine_final_recommendations(self, weighted_evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """最終推奨決定（◎○▲×）"""
        try:
            final_score = weighted_evaluation.get('final_score', 0)
            grade = weighted_evaluation.get('evaluation_grade', 'F')
            
            # 模擬的な推奨馬生成（実際は各分析結果から統合）
            recommendations = []
            
            if final_score >= 85:
                # S級評価: 強い推奨
                recommendations = [
                    {
                        'recommendation_type': '◎',
                        'horse_name': '本命馬',
                        'horse_number': 1,
                        'final_score': final_score,
                        'confidence': 'very_high',
                        'reasoning': 'すべての分析で高評価',
                        'investment_priority': 'high'
                    },
                    {
                        'recommendation_type': '○',
                        'horse_name': '対抗馬',
                        'horse_number': 2,
                        'final_score': final_score - 5,
                        'confidence': 'high',
                        'reasoning': '複数分析で好評価',
                        'investment_priority': 'medium'
                    }
                ]
            elif final_score >= 70:
                # A級評価: 中程度の推奨
                recommendations = [
                    {
                        'recommendation_type': '○',
                        'horse_name': '本命馬',
                        'horse_number': 1,
                        'final_score': final_score,
                        'confidence': 'high',
                        'reasoning': '総合的に安定した評価',
                        'investment_priority': 'medium'
                    },
                    {
                        'recommendation_type': '▲',
                        'horse_name': '単穴馬',
                        'horse_number': 3,
                        'final_score': final_score - 8,
                        'confidence': 'medium',
                        'reasoning': '特定条件で期待値高',
                        'investment_priority': 'low'
                    }
                ]
            else:
                # 低評価: 投資見送り推奨
                recommendations = [
                    {
                        'recommendation_type': '×',
                        'horse_name': '見送り',
                        'horse_number': 0,
                        'final_score': final_score,
                        'confidence': 'low',
                        'reasoning': '投資条件を満たさず',
                        'investment_priority': 'none'
                    }
                ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Final recommendations determination error: {str(e)}")
            return []

    def _generate_detailed_report(self, race_data: Dict[str, Any], 
                                analysis_results: List[Any],
                                integration_results: Dict[str, Any],
                                recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """詳細分析レポート生成"""
        try:
            report = {
                'race_overview': self._create_race_overview(race_data),
                'analysis_summary': self._create_analysis_summary(analysis_results),
                'key_factors': self._identify_key_factors(analysis_results),
                'risk_assessment': self._create_risk_assessment(analysis_results),
                'market_analysis': self._create_market_analysis(integration_results),
                'recommendation_rationale': self._create_recommendation_rationale(recommendations),
                'alternative_scenarios': self._create_alternative_scenarios(analysis_results)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Detailed report generation error: {str(e)}")
            return {}

    def _create_race_overview(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """レース概要作成"""
        return {
            'race_name': race_data.get('race_name', '不明'),
            'track': race_data.get('track', '不明'),
            'distance': race_data.get('distance', '不明'),
            'surface': race_data.get('surface', '不明'),
            'condition': race_data.get('condition', '不明'),
            'horse_count': len(race_data.get('horses', [])),
            'grade': race_data.get('grade', ''),
            'weather': race_data.get('weather', '不明')
        }

    def _create_analysis_summary(self, analysis_results: List[Any]) -> Dict[str, Any]:
        """分析サマリー作成"""
        summary = {}
        
        for result in analysis_results:
            summary[result.module_name] = {
                'score': result.score,
                'weight': result.weight,
                'status': result.status,
                'execution_time': result.execution_time,
                'key_insights': self._extract_key_insights(result.details)
            }
        
        return summary

    def _extract_key_insights(self, details: Dict[str, Any]) -> List[str]:
        """主要洞察抽出"""
        insights = []
        
        # 詳細データから重要なポイントを抽出
        if isinstance(details, dict):
            for key, value in details.items():
                if key in ['top_recommendations', 'special_combinations', 'risk_factors']:
                    insights.append(f"{key}: {str(value)[:100]}...")
        
        return insights[:3]  # 最大3つまで

    def _score_to_grade(self, score: float) -> str:
        """スコアをグレードに変換"""
        if score >= 90:
            return 'S+'
        elif score >= 85:
            return 'S'
        elif score >= 80:
            return 'A+'
        elif score >= 75:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 65:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'

    def _calculate_quality_score(self, analysis_results: List[Any]) -> float:
        """品質スコア計算
            def _calculate_quality_score(self, analysis_results: List[Any]) -> float:
        """品質スコア計算"""
        try:
            if not analysis_results:
                return 0.0
            
            total_quality = 0
            successful_modules = 0
            
            for result in analysis_results:
                if result.status == 'completed':
                    # 実行時間による品質評価
                    time_quality = min(1.0, 30 / max(1, result.execution_time))
                    
                    # スコアの妥当性による品質評価
                    score_quality = 1.0 if 0 <= result.score <= 100 else 0.5
                    
                    # 詳細データの充実度
                    detail_quality = min(1.0, len(str(result.details)) / 1000)
                    
                    module_quality = (time_quality * 0.3 + score_quality * 0.4 + detail_quality * 0.3)
                    total_quality += module_quality
                    successful_modules += 1
                else:
                    # エラーモジュールは品質0
                    total_quality += 0
                    successful_modules += 1
            
            return (total_quality / successful_modules * 100) if successful_modules > 0 else 0
            
        except Exception as e:
            logger.error(f"Quality score calculation error: {str(e)}")
            return 0.0

    def _calculate_overall_confidence(self, analysis_results: List[Any]) -> float:
        """総合信頼度計算"""
        try:
            total_confidence = 0
            total_weight = 0
            
            for result in analysis_results:
                if result.status == 'completed':
                    # モジュールの重みと成功率を考慮
                    weight = result.weight
                    confidence = min(1.0, result.score / 100)
                    
                    total_confidence += confidence * weight
                    total_weight += weight
            
            return total_confidence / total_weight if total_weight > 0 else 0
            
        except Exception as e:
            logger.error(f"Overall confidence calculation error: {str(e)}")
            return 0.0

    def _identify_key_factors(self, analysis_results: List[Any]) -> List[Dict[str, Any]]:
        """主要要因特定"""
        key_factors = []
        
        try:
            for result in analysis_results:
                if result.status == 'completed' and result.score >= 70:
                    factor = {
                        'factor_type': result.module_name,
                        'importance': result.weight,
                        'score': result.score,
                        'impact': 'positive' if result.score >= 70 else 'negative',
                        'description': self._get_factor_description(result)
                    }
                    key_factors.append(factor)
            
            # 重要度順でソート
            key_factors.sort(key=lambda x: x['importance'], reverse=True)
            return key_factors[:5]  # 上位5要因
            
        except Exception as e:
            logger.error(f"Key factors identification error: {str(e)}")
            return []

    def _get_factor_description(self, result: Any) -> str:
        """要因説明生成"""
        descriptions = {
            'jockey_trainer': '騎手と厩舎の相性が良好',
            'basic_analysis': '基本的な競走能力が高い',
            'ability_analysis': '実戦での能力発揮が期待される',
            'bloodline': '血統的に適性が高い',
            'performance_rate': '連対率の実績が安定している',
            'dark_horse': '穴馬としての期待値が高い',
            'pre_race_info': '直前情報が好材料',
            'market_efficiency': '市場評価に対して割安'
        }
        
        return descriptions.get(result.module_name, '詳細分析で高評価')

    def _create_risk_assessment(self, analysis_results: List[Any]) -> Dict[str, Any]:
        """リスク評価作成"""
        try:
            risk_factors = []
            overall_risk = 'medium'
            
            # 各モジュールからリスク要因を抽出
            for result in analysis_results:
                if hasattr(result, 'details') and isinstance(result.details, dict):
                    if 'risk_factors' in result.details:
                        risk_factors.extend(result.details['risk_factors'])
            
            # リスクレベル判定
            high_risk_count = sum(1 for factor in risk_factors if 'high' in str(factor).lower())
            
            if high_risk_count >= 3:
                overall_risk = 'high'
            elif high_risk_count == 0:
                overall_risk = 'low'
            
            return {
                'overall_risk': overall_risk,
                'risk_factors': risk_factors[:10],  # 最大10要因
                'risk_mitigation': self._suggest_risk_mitigation(risk_factors),
                'confidence_adjustment': self._calculate_risk_adjustment(overall_risk)
            }
            
        except Exception as e:
            logger.error(f"Risk assessment creation error: {str(e)}")
            return {'overall_risk': 'medium', 'risk_factors': []}

    def _suggest_risk_mitigation(self, risk_factors: List[str]) -> List[str]:
        """リスク軽減策提案"""
        suggestions = []
        
        if '格上挑戦' in risk_factors:
            suggestions.append('投資額を控えめに設定')
        if '休み明け' in risk_factors:
            suggestions.append('複勝中心の手堅い投資')
        if '距離延長' in risk_factors or '距離短縮' in risk_factors:
            suggestions.append('距離適性を慎重に検討')
        
        return suggestions[:3]

    def _calculate_risk_adjustment(self, risk_level: str) -> float:
        """リスク調整係数計算"""
        adjustments = {'low': 1.0, 'medium': 0.9, 'high': 0.7}
        return adjustments.get(risk_level, 0.9)

    def _create_market_analysis(self, integration_results: Dict[str, Any]) -> Dict[str, Any]:
        """市場分析作成"""
        try:
            market_efficiency = integration_results.get('market_efficiency', {})
            
            return {
                'market_sentiment': market_efficiency.get('market_sentiment', 'neutral'),
                'value_opportunities': market_efficiency.get('undervalued_horses', []),
                'overvalued_risks': market_efficiency.get('overvalued_horses', []),
                'odds_analysis': market_efficiency.get('odds_analysis', {}),
                'betting_trends': market_efficiency.get('betting_trends', {})
            }
            
        except Exception as e:
            logger.error(f"Market analysis creation error: {str(e)}")
            return {}

    def _create_recommendation_rationale(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """推奨根拠作成"""
        try:
            rationale = {}
            
            for rec in recommendations:
                rec_type = rec.get('recommendation_type', '')
                rationale[rec_type] = {
                    'horse_name': rec.get('horse_name', ''),
                    'primary_reason': rec.get('reasoning', ''),
                    'supporting_factors': self._get_supporting_factors(rec),
                    'confidence_level': rec.get('confidence', 'medium'),
                    'expected_performance': self._predict_performance(rec)
                }
            
            return rationale
            
        except Exception as e:
            logger.error(f"Recommendation rationale creation error: {str(e)}")
            return {}

    def _get_supporting_factors(self, recommendation: Dict[str, Any]) -> List[str]:
        """支持要因取得"""
        # 簡略化実装
        return [
            '複数の分析で高評価',
            '騎手厩舎の相性良好',
            '適距離での実績'
        ]

    def _predict_performance(self, recommendation: Dict[str, Any]) -> str:
        """成績予測"""
        confidence = recommendation.get('confidence', 'medium')
        
        if confidence == 'very_high':
            return '1-3着内濃厚'
        elif confidence == 'high':
            return '上位入線期待'
        elif confidence == 'medium':
            return '健闘期待'
        else:
            return '厳しい戦い'

    def _create_alternative_scenarios(self, analysis_results: List[Any]) -> Dict[str, Any]:
        """代替シナリオ作成"""
        return {
            'best_case': '全ての好材料が揃った場合の期待成績',
            'worst_case': 'リスク要因が顕在化した場合の想定',
            'most_likely': '現実的に期待される結果',
            'upset_potential': '波乱の可能性と要因'
        }

    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """エラー結果作成"""
        return {
            'status': 'error',
            'error_message': error_msg,
            'recommendations': [],
            'quality_score': 0,
            'confidence_level': 0
        }
