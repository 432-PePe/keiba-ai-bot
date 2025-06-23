import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import statistics

logger = logging.getLogger(__name__)

@dataclass
class LearningMetrics:
    """学習指標データクラス"""
    prediction_accuracy: float
    hit_rate: float
    roi: float
    confidence_calibration: float
    model_drift_score: float
    improvement_score: float

class LearningImprovement:
    """学習改善システム v3.1【AI的学習改善・バックテスト統合】"""
    
    def __init__(self):
        self.max_analysis_time = 28  # 秒
        
        # 学習評価の重み配分
        self.learning_weights = {
            'prediction_accuracy': 0.30,    # 予想精度
            'hit_rate_analysis': 0.25,      # 的中率分析
            'roi_performance': 0.20,        # 投資収益率
            'model_stability': 0.15,        # モデル安定性
            'adaptation_speed': 0.10        # 適応速度
        }
        
        # 改善対象モジュール
        self.target_modules = [
            'basic_analysis', 'jockey_trainer', 'bloodline', 'ability_analysis',
            'performance_rate', 'dark_horse', 'market_efficiency', 'pre_race_info'
        ]
        
        # 学習データ保存期間
        self.learning_data_retention = {
            'detailed_results': 30,      # 詳細結果: 30日
            'aggregated_metrics': 90,    # 集計指標: 90日
            'model_parameters': 365      # モデルパラメータ: 365日
        }

    async def analyze(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """学習改善分析実行（28秒）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting learning improvement analysis v3.1")
        
        try:
            # 過去の予想結果データ取得
            historical_data = await self._get_historical_prediction_data()
            
            if not historical_data:
                return self._create_initial_learning_result()
            
            # 予想精度分析
            accuracy_analysis = await self._analyze_prediction_accuracy(historical_data)
            
            # 的中率パターン分析
            hit_rate_analysis = await self._analyze_hit_rate_patterns(historical_data)
            
            # ROI（投資収益率）分析
            roi_analysis = await self._analyze_roi_performance(historical_data)
            
            # モデル安定性評価
            stability_analysis = await self._evaluate_model_stability(historical_data)
            
            # 適応性能分析
            adaptation_analysis = await self._analyze_adaptation_performance(historical_data)
            
            # 改善提案生成
            improvement_proposals = await self._generate_improvement_proposals(
                accuracy_analysis, hit_rate_analysis, roi_analysis, stability_analysis
            )
            
            # パラメータ最適化提案
            parameter_optimization = await self._propose_parameter_optimization(historical_data)
            
            # 学習スケジュール更新
            learning_schedule = self._update_learning_schedule(improvement_proposals)
            
            # 総合学習スコア
            overall_learning_score = self._calculate_overall_learning_score(
                accuracy_analysis, hit_rate_analysis, roi_analysis, stability_analysis, adaptation_analysis
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Learning improvement analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'learning_score': overall_learning_score,
                'accuracy_analysis': accuracy_analysis,
                'hit_rate_analysis': hit_rate_analysis,
                'roi_analysis': roi_analysis,
                'stability_analysis': stability_analysis,
                'adaptation_analysis': adaptation_analysis,
                'improvement_proposals': improvement_proposals,
                'parameter_optimization': parameter_optimization,
                'learning_schedule': learning_schedule,
                'learning_summary': self._create_learning_summary(
                    overall_learning_score, improvement_proposals, parameter_optimization
                )
            }
            
        except Exception as e:
            logger.error(f"Learning improvement analysis error: {str(e)}")
            return self._create_error_result(str(e))

    async def _get_historical_prediction_data(self) -> List[Dict[str, Any]]:
        """過去の予想結果データ取得"""
        try:
            # 実際の実装ではデータベースから取得
            # ここでは模擬データを使用
            
            historical_data = []
            
            # 過去30日分の模擬予想結果
            for i in range(30):
                prediction_date = datetime.now() - timedelta(days=i+1)
                
                # 1日あたり3-5レースの予想結果を生成
                daily_races = 3 + (i % 3)
                
                for race_num in range(daily_races):
                    race_result = self._generate_mock_race_result(prediction_date, race_num + 1)
                    historical_data.append(race_result)
            
            logger.info(f"Retrieved {len(historical_data)} historical prediction records")
            return historical_data
            
        except Exception as e:
            logger.error(f"Historical data retrieval error: {str(e)}")
            return []

    def _generate_mock_race_result(self, date: datetime, race_number: int) -> Dict[str, Any]:
        """模擬レース結果生成"""
        import random
        
        # 日付ベースのシード設定で一貫性を保つ
        random.seed(int(date.timestamp()) + race_number)
        
        # 予想結果の生成
        predicted_horses = [
            {'horse_name': f'予想馬{i}', 'predicted_rank': i, 'confidence': 0.9 - i*0.1, 'odds': 2.0 + i*1.5}
            for i in range(1, 4)  # 上位3頭の予想
        ]
        
        # 実際の結果（的中率を調整）
        hit_success = random.random() < 0.35  # 35%の的中率
        
        if hit_success:
            actual_result = [1, 2, 3]  # 予想通り
            roi = random.uniform(110, 150)  # 110-150%のROI
        else:
            actual_result = [random.randint(4, 12) for _ in range(3)]  # 外れ
            roi = 0  # 損失
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'race_number': race_number,
            'predicted_horses': predicted_horses,
            'actual_result': actual_result,
            'hit_success': hit_success,
            'roi': roi,
            'investment_amount': 1000,
            'return_amount': roi * 10 if hit_success else 0,
            'module_scores': {
                'basic_analysis': random.uniform(60, 90),
                'jockey_trainer': random.uniform(65, 85),
                'bloodline': random.uniform(50, 80),
                'ability_analysis': random.uniform(55, 85)
            }
        }

    async def _analyze_prediction_accuracy(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """予想精度分析"""
        try:
            if not historical_data:
                return {'accuracy_score': 0, 'trend': 'insufficient_data'}
            
            # 全体的中率
            total_predictions = len(historical_data)
            successful_hits = sum(1 for record in historical_data if record.get('hit_success', False))
            overall_hit_rate = successful_hits / total_predictions if total_predictions > 0 else 0
            
            # 期間別的中率トレンド分析
            recent_data = historical_data[:10]  # 直近10レース
            recent_hit_rate = sum(1 for record in recent_data if record.get('hit_success', False)) / len(recent_data)
            
            older_data = historical_data[10:20] if len(historical_data) > 10 else []
            older_hit_rate = sum(1 for record in older_data if record.get('hit_success', False)) / len(older_data) if older_data else recent_hit_rate
            
            # トレンド判定
            if recent_hit_rate > older_hit_rate + 0.05:
                trend = 'improving'
            elif recent_hit_rate < older_hit_rate - 0.05:
                trend = 'declining'
            else:
                trend = 'stable'
            
            # 信頼度校正分析
            confidence_calibration = self._analyze_confidence_calibration(historical_data)
            
            # 精度スコア計算
            accuracy_score = (
                overall_hit_rate * 60 +
                confidence_calibration * 40
            )
            
            return {
                'accuracy_score': accuracy_score,
                'overall_hit_rate': overall_hit_rate,
                'recent_hit_rate': recent_hit_rate,
                'older_hit_rate': older_hit_rate,
                'trend': trend,
                'confidence_calibration': confidence_calibration,
                'total_predictions': total_predictions,
                'successful_hits': successful_hits,
                'accuracy_assessment': self._assess_accuracy_level(overall_hit_rate)
            }
            
        except Exception as e:
            logger.error(f"Prediction accuracy analysis error: {str(e)}")
            return {'accuracy_score': 0, 'trend': 'error'}

    async def _analyze_hit_rate_patterns(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """的中率パターン分析"""
        try:
            # 条件別的中率分析
            patterns = {
                'by_confidence': self._analyze_hit_rate_by_confidence(historical_data),
                'by_odds_range': self._analyze_hit_rate_by_odds(historical_data),
                'by_day_of_week': self._analyze_hit_rate_by_day(historical_data),
                'by_module_strength': self._analyze_hit_rate_by_modules(historical_data)
            }
            
            # パターン強度評価
            pattern_strength = self._evaluate_pattern_strength(patterns)
            
            # 改善機会特定
            improvement_opportunities = self._identify_hit_rate_improvements(patterns)
            
            # パターンスコア計算
            pattern_score = sum(pattern.get('score', 50) for pattern in patterns.values()) / len(patterns)
            
            return {
                'pattern_score': pattern_score,
                'patterns': patterns,
                'pattern_strength': pattern_strength,
                'improvement_opportunities': improvement_opportunities,
                'pattern_insights': self._generate_pattern_insights(patterns)
            }
            
        except Exception as e:
            logger.error(f"Hit rate patterns analysis error: {str(e)}")
            return {'pattern_score': 50, 'patterns': {}}

    async def _analyze_roi_performance(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """ROI（投資収益率）分析"""
        try:
            # 全投資データの集計
            total_investment = sum(record.get('investment_amount', 0) for record in historical_data)
            total_return = sum(record.get('return_amount', 0) for record in historical_data)
            
            overall_roi = (total_return / total_investment * 100) if total_investment > 0 else 0
            
            # 期間別ROI分析
            roi_trends = self._analyze_roi_trends(historical_data)
            
            # 投資効率分析
            investment_efficiency = self._analyze_investment_efficiency(historical_data)
            
            # リスク調整リターン
            risk_adjusted_return = self._calculate_risk_adjusted_return(historical_data)
            
            # ROIスコア計算
            roi_score = min(100, max(0, overall_roi))
            
            return {
                'roi_score': roi_score,
                'overall_roi': overall_roi,
                'total_investment': total_investment,
                'total_return': total_return,
                'profit_loss': total_return - total_investment,
                'roi_trends': roi_trends,
                'investment_efficiency': investment_efficiency,
                'risk_adjusted_return': risk_adjusted_return,
                'roi_assessment': self._assess_roi_performance(overall_roi)
            }
            
        except Exception as e:
            logger.error(f"ROI analysis error: {str(e)}")
            return {'roi_score': 0, 'overall_roi': 0}

    async def _evaluate_model_stability(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """モデル安定性評価"""
        try:
            # 各モジュールのスコア安定性分析
            module_stability = {}
            
            for module in self.target_modules:
                module_scores = []
                for record in historical_data:
                    module_scores_dict = record.get('module_scores', {})
                    if module in module_scores_dict:
                        module_scores.append(module_scores_dict[module])
                
                if module_scores:
                    stability_score = self._calculate_stability_score(module_scores)
                    module_stability[module] = {
                        'stability_score': stability_score,
                        'average_score': statistics.mean(module_scores),
                        'score_variance': statistics.variance(module_scores) if len(module_scores) > 1 else 0,
                        'trend': self._analyze_module_trend(module_scores)
                    }
            
            # 全体的安定性
            overall_stability = statistics.mean([
                module_data['stability_score'] 
                for module_data in module_stability.values()
            ]) if module_stability else 50
            
            # ドリフト検出
            model_drift = self._detect_model_drift(historical_data)
            
            return {
                'stability_score': overall_stability,
                'module_stability': module_stability,
                'model_drift': model_drift,
                'stability_assessment': self._assess_stability_level(overall_stability),
                'stability_recommendations': self._generate_stability_recommendations(module_stability)
            }
            
        except Exception as e:
            logger.error(f"Model stability evaluation error: {str(e)}")
            return {'stability_score': 50, 'model_drift': 'unknown'}

    async def _generate_improvement_proposals(self, accuracy_analysis: Dict, hit_rate_analysis: Dict, 
                                            roi_analysis: Dict, stability_analysis: Dict) -> List[Dict[str, Any]]:
        """改善提案生成"""
        try:
            proposals = []
            
            # 精度改善提案
            if accuracy_analysis.get('accuracy_score', 0) < 70:
                proposals.append({
                    'type': 'accuracy_improvement',
                    'priority': 'high',
                    'target_module': 'basic_analysis',
                    'proposal': '基本分析の重み配分を調整し、より実績重視の評価に変更',
                    'expected_impact': '的中率5-8%向上',
                    'implementation_effort': 'medium'
                })
            
            # ROI改善提案
            if roi_analysis.get('overall_roi', 0) < 110:
                proposals.append({
                    'type': 'roi_improvement',
                    'priority': 'high',
                    'target_module': 'investment_calc',
                    'proposal': 'ケリー基準の保守係数を調整し、より積極的な投資戦略に変更',
                    'expected_impact': 'ROI10-15%向上',
                    'implementation_effort': 'low'
                })
            
            # 安定性改善提案
            unstable_modules = [
                module for module, data in stability_analysis.get('module_stability', {}).items()
                if data.get('stability_score', 50) < 60
            ]
            
            if unstable_modules:
                proposals.append({
                    'type': 'stability_improvement',
                    'priority': 'medium',
                    'target_module': unstable_modules[0],
                    'proposal': f'{unstable_modules[0]}モジュールの評価ロジックを見直し、より安定した指標に変更',
                    'expected_impact': '予想の一貫性向上',
                    'implementation_effort': 'high'
                })
            
            # パターン活用提案
            improvement_opportunities = hit_rate_analysis.get('improvement_opportunities', [])
            if improvement_opportunities:
                proposals.append({
                    'type': 'pattern_optimization',
                    'priority': 'medium',
                    'target_module': 'multiple',
                    'proposal': f'発見されたパターン（{improvement_opportunities[0]}）を活用した重み調整',
                    'expected_impact': '特定条件下での的中率向上',
                    'implementation_effort': 'medium'
                })
            
            # 提案の優先度でソート
            proposals.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
            
            return proposals[:5]  # 最大5つの提案
            
        except Exception as e:
            logger.error(f"Improvement proposals generation error: {str(e)}")
            return []

    def _calculate_overall_learning_score(self, accuracy_analysis: Dict, hit_rate_analysis: Dict, 
                                        roi_analysis: Dict, stability_analysis: Dict, 
                                        adaptation_analysis: Dict) -> float:
        """総合学習スコア計算"""
        try:
            accuracy_score = accuracy_analysis.get('accuracy_score', 0)
            pattern_score = hit_rate_analysis.get('pattern_score', 50)
            roi_score = roi_analysis.get('roi_score', 0)
            stability_score = stability_analysis.get('stability_score', 50)
            adaptation_score = adaptation_analysis.get('adaptation_score', 50)
            
            # 重み付き計算
            total_score = (
                accuracy_score * self.learning_weights['prediction_accuracy'] +
                pattern_score * self.learning_weights['hit_rate_analysis'] +
                roi_score * self.learning_weights['roi_performance'] +
                stability_score * self.learning_weights['model_stability'] +
                adaptation_score * self.learning_weights['adaptation_speed']
            )
            
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"Overall learning score calculation error: {str(e)}")
            return 50.0

    # ヘルパーメソッド
    def _analyze_confidence_calibration(self, historical_data: List[Dict]) -> float:
        """信頼度校正分析"""
        try:
            # 信頼度と実際の的中率の一致度を評価
            confidence_buckets = {'high': [], 'medium': [], 'low': []}
            
            for record in historical_data:
                predicted_horses = record.get('predicted_horses', [])
                hit_success = record.get('hit_success', False)
                
                if predicted_horses:
                    confidence = predicted_horses[0].get('confidence', 0.5)
                    
                    if confidence >= 0.8:
                        confidence_buckets['high'].append(hit_success)
                    elif confidence >= 0.6:
                        confidence_buckets['medium'].append(hit_success)
                    else:
                        confidence_buckets['low'].append(hit_success)
            
            # 各信頼度レベルでの的中率
            calibration_score = 0
            bucket_count = 0
            
            for level, results in confidence_buckets.items():
                if results:
                    actual_hit_rate = sum(results) / len(results)
                    expected_hit_rate = {'high': 0.8, 'medium': 0.6, 'low': 0.4}[level]
                    
                    # 期待値との差の逆数をスコア化
                    calibration_score += max(0, 100 - abs(actual_hit_rate - expected_hit_rate) * 200)
                    bucket_count += 1
            
            return calibration_score / bucket_count if bucket_count > 0 else 50
            
        except Exception as e:
            logger.error(f"Confidence calibration analysis error: {str(e)}")
            return 50.0

    def _calculate_stability_score(self, scores: List[float]) -> float:
        """安定性スコア計算"""
        try:
            if len(scores) < 2:
                return 50.0
            
            # 標準偏差の逆数をベースにしたスコア
            std_dev = statistics.stdev(scores)
            stability_score = max(0, 100 - std_dev * 2)  # 標準偏差が大きいほどスコアが低下
            
            return stability_score
            
        except Exception as e:
            return 50.0

    def _create_initial_learning_result(self) -> Dict[str, Any]:
        """初期学習結果作成"""
        return {
            'status': 'initial_state',
            'message': '学習データが不足しています。予想実行を継続してデータを蓄積してください。',
            'learning_score': 50,
            'recommendations': ['予想実行の継続', 'データ蓄積期間の確保']
        }

    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """エラー結果作成"""
        return {
            'status': 'error',
            'error_message': error_msg,
            'learning_score': 0,
            'execution_time': 0
        }

    # ... その他のヘルパーメソッドは実装省略（実際の開発時に詳細実装）
    async def _analyze_adaptation_performance(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """適応性能分析"""
        return {'adaptation_score': 50.0, 'adaptation_speed': 'moderate'}

    def _update_learning_schedule(self, proposals: List[Dict]) -> Dict[str, Any]:
        """学習スケジュール更新"""
        return {'next_update': '7日後', 'priority_items': [p['type'] for p in proposals[:3]]}

    # ... その他も同様に簡略化実装
