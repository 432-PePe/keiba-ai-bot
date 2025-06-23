import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
import concurrent.futures
from dataclasses import dataclass

from .race_collector import RaceCollector
from .basic_analysis import BasicAnalysis
from .jockey_trainer import JockeyTrainerAnalysis
from .performance_rate import PerformanceRateAnalysis
from .bloodline import BloodlineAnalysis
from .ability_analysis import AbilityAnalysis
from .dark_horse import DarkHorseAnalysis
from .market_efficiency import MarketEfficiencyAnalysis
from .pre_race_info import PreRaceInfoAnalysis
from .data_validation import DataValidation
from .learning_improvement import LearningImprovement
from .investment_calc import InvestmentCalculator
from .integrated_output import IntegratedOutput
from .challenge_judgment import ChallengeJudgment

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """分析結果データクラス"""
    module_name: str
    weight: float
    score: float
    details: Dict[str, Any]
    execution_time: float
    status: str

class MainController:
    """AI競馬予想システム v3.1 メインコントローラー"""
    
    def __init__(self):
        self.max_execution_time = 225  # 秒
        self.daily_investment_limit = 20000  # 円
        
        # 各分析モジュールの重み設定
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
        
        # モジュール初期化
        self.race_collector = RaceCollector()
        self.basic_analysis = BasicAnalysis()
        self.jockey_trainer = JockeyTrainerAnalysis()
        self.performance_rate = PerformanceRateAnalysis()
        self.bloodline = BloodlineAnalysis()
        self.ability_analysis = AbilityAnalysis()
        self.dark_horse = DarkHorseAnalysis()
        self.market_efficiency = MarketEfficiencyAnalysis()
        self.pre_race_info = PreRaceInfoAnalysis()
        self.data_validation = DataValidation()
        self.learning_improvement = LearningImprovement()
        self.investment_calc = InvestmentCalculator()
        self.integrated_output = IntegratedOutput()
        self.challenge_judgment = ChallengeJudgment()
        
        logger.info("MainController initialized with v3.1 specifications")

    async def execute_full_analysis(self) -> Dict[str, Any]:
        """完全分析実行（225秒以内）"""
        start_time = time.time()
        
        try:
            logger.info("Starting full AI analysis v3.1")
            
            # Phase 0: Critical問題対策・完全情報収集（75秒）
            race_data = await self._phase_0_data_collection()
            if not race_data:
                return self._create_error_response("Phase 0: Data collection failed")
            
            # Phase 1: 基本分析（35秒・20%重み）
            basic_result = await self._phase_1_basic_analysis(race_data)
            
            # Phase 2: 専門分析（150秒）
            specialist_results = await self._phase_2_specialist_analysis(race_data)
            
            # Phase 3: 新機能統合（30秒）
            integration_results = await self._phase_3_integration(race_data)
            
            # Phase 4: 品質管理・統合評価（35秒）
            final_evaluation = await self._phase_4_evaluation(
                race_data, basic_result, specialist_results, integration_results
            )
            
            # Phase 5: 科学的投資戦略（25秒）
            investment_strategy = await self._phase_5_investment(final_evaluation)
            
            execution_time = time.time() - start_time
            logger.info(f"Full analysis completed in {execution_time:.2f} seconds")
            
            return self._create_success_response(
                final_evaluation, investment_strategy, execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in full analysis: {str(e)}")
            return self._create_error_response(f"Analysis failed: {str(e)}")

    async def _phase_0_data_collection(self) -> Optional[Dict[str, Any]]:
        """Phase 0: Critical問題対策・完全情報収集（75秒）"""
        logger.info("Phase 0: Starting data collection")
        
        try:
            # 文字化け対策・完全情報収集
            race_data = await self.race_collector.collect_all_races()
            
            # データ品質検証
            validation_result = self.data_validation.validate_race_data(race_data)
            
            if not validation_result['is_valid']:
                logger.error(f"Data validation failed: {validation_result['errors']}")
                return None
            
            logger.info(f"Phase 0 completed: {len(race_data)} races collected")
            return race_data
            
        except Exception as e:
            logger.error(f"Phase 0 error: {str(e)}")
            return None

    async def _phase_1_basic_analysis(self, race_data: Dict[str, Any]) -> AnalysisResult:
        """Phase 1: 基本分析（35秒・20%重み）"""
        logger.info("Phase 1: Starting basic analysis")
        
        start_time = time.time()
        
        try:
            # 人気馬必須詳細分析 + 格上挑戦判定 + 市場評価統合
            analysis_result = await self.basic_analysis.analyze(race_data)
            
            # 格上挑戦判定システム統合
            challenge_result = await self.challenge_judgment.evaluate(race_data)
            analysis_result['challenge_judgment'] = challenge_result
            
            execution_time = time.time() - start_time
            
            return AnalysisResult(
                module_name='basic_analysis',
                weight=self.module_weights['basic_analysis'],
                score=analysis_result.get('total_score', 0),
                details=analysis_result,
                execution_time=execution_time,
                status='completed'
            )
            
        except Exception as e:
            logger.error(f"Phase 1 error: {str(e)}")
            return self._create_error_result('basic_analysis', str(e))

    async def _phase_2_specialist_analysis(self, race_data: Dict[str, Any]) -> List[AnalysisResult]:
        """Phase 2: 専門分析（150秒）"""
        logger.info("Phase 2: Starting specialist analysis")
        
        # 並行実行でパフォーマンス向上
        tasks = [
            self._run_jockey_trainer_analysis(race_data),      # 40秒・22%重み
            self._run_ability_analysis(race_data),             # 45秒・20%重み  
            self._run_bloodline_analysis(race_data),           # 35秒・15%重み
            self._run_performance_rate_analysis(race_data),    # 25秒・15%重み
            self._run_dark_horse_analysis(race_data),          # 10秒・5%重み
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # エラーハンドリング
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Specialist analysis error: {result}")
                continue
            valid_results.append(result)
        
        logger.info(f"Phase 2 completed: {len(valid_results)} analyses")
        return valid_results

    async def _run_jockey_trainer_analysis(self, race_data: Dict[str, Any]) -> AnalysisResult:
        """騎手厩舎相性分析（40秒・22%重み）"""
        start_time = time.time()
        
        try:
            result = await self.jockey_trainer.analyze(race_data)
            execution_time = time.time() - start_time
            
            return AnalysisResult(
                module_name='jockey_trainer',
                weight=self.module_weights['jockey_trainer'],
                score=result.get('compatibility_score', 0),
                details=result,
                execution_time=execution_time,
                status='completed'
            )
        except Exception as e:
            return self._create_error_result('jockey_trainer', str(e))

    async def _run_ability_analysis(self, race_data: Dict[str, Any]) -> AnalysisResult:
        """実戦能力分析（45秒・18%重み）"""
        start_time = time.time()
        
        try:
            result = await self.ability_analysis.analyze(race_data)
            execution_time = time.time() - start_time
            
            return AnalysisResult(
                module_name='ability_analysis',
                weight=self.module_weights['ability_analysis'],
                score=result.get('ability_score', 0),
                details=result,
                execution_time=execution_time,
                status='completed'
            )
        except Exception as e:
            return self._create_error_result('ability_analysis', str(e))

    async def _run_bloodline_analysis(self, race_data: Dict[str, Any]) -> AnalysisResult:
        """血統適性分析（35秒・15%重み）"""
        start_time = time.time()
        
        try:
            result = await self.bloodline.analyze(race_data)
            execution_time = time.time() - start_time
            
            return AnalysisResult(
                module_name='bloodline',
                weight=self.module_weights['bloodline'],
                score=result.get('bloodline_score', 0),
                details=result,
                execution_time=execution_time,
                status='completed'
            )
        except Exception as e:
            return self._create_error_result('bloodline', str(e))

    async def _run_performance_rate_analysis(self, race_data: Dict[str, Any]) -> AnalysisResult:
        """連帯率実績分析（25秒・15%重み）"""
        start_time = time.time()
        
        try:
            result = await self.performance_rate.analyze(race_data)
            execution_time = time.time() - start_time
            
            return AnalysisResult(
                module_name='performance_rate',
                weight=self.module_weights['performance_rate'],
                score=result.get('performance_score', 0),
                details=result,
                execution_time=execution_time,
                status='completed'
            )
        except Exception as e:
            return self._create_error_result('performance_rate', str(e))

    async def _run_dark_horse_analysis(self, race_data: Dict[str, Any]) -> AnalysisResult:
        """穴馬発掘分析（10秒・5%重み）"""
        start_time = time.time()
        
        try:
            result = await self.dark_horse.analyze(race_data)
            execution_time = time.time() - start_time
            
            return AnalysisResult(
                module_name='dark_horse',
                weight=self.module_weights['dark_horse'],
                score=result.get('dark_horse_score', 0),
                details=result,
                execution_time=execution_time,
                status='completed'
            )
        except Exception as e:
            return self._create_error_result('dark_horse', str(e))

    async def _phase_3_integration(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: 新機能統合（30秒）"""
        logger.info("Phase 3: Starting integration analysis")
        
        try:
            # 市場効率性分析（15秒・新機能）
            market_result = await self.market_efficiency.analyze(race_data)
            
            # 直前情報分析（5秒・3%重み）
            pre_race_result = await self.pre_race_info.analyze(race_data)
            
            return {
                'market_efficiency': market_result,
                'pre_race_info': pre_race_result
            }
            
        except Exception as e:
            logger.error(f"Phase 3 error: {str(e)}")
            return {}

    async def _phase_4_evaluation(self, race_data: Dict[str, Any], 
                                basic_result: AnalysisResult,
                                specialist_results: List[AnalysisResult],
                                integration_results: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: 品質管理・統合評価（35秒）"""
        logger.info("Phase 4: Starting evaluation")
        
        try:
            # 全分析結果の統合
            all_results = [basic_result] + specialist_results
            
            # 重み付き統合評価
            integrated_evaluation = await self.integrated_output.generate(
                race_data, all_results, integration_results
            )
            
            # データ検証
            validation_result = self.data_validation.validate_analysis_results(
                integrated_evaluation
            )
            
            integrated_evaluation['validation'] = validation_result
            
            return integrated_evaluation
            
        except Exception as e:
            logger.error(f"Phase 4 error: {str(e)}")
            return {}

    async def _phase_5_investment(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 5: 科学的投資戦略（25秒）"""
        logger.info("Phase 5: Starting investment calculation")
        
        try:
            # ケリー基準 + リスク分散強化
            investment_strategy = await self.investment_calc.calculate(
                evaluation, self.daily_investment_limit
            )
            
            return investment_strategy
            
        except Exception as e:
            logger.error(f"Phase 5 error: {str(e)}")
            return {}

    def execute_daily_prediction(self) -> List[Dict[str, Any]]:
        """日次予想実行（同期版）"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.execute_full_analysis())
            loop.close()
            
            if result.get('status') == 'success':
                return result.get('predictions', [])
            return []
            
        except Exception as e:
            logger.error(f"Daily prediction error: {str(e)}")
            return []

    def execute_race_analysis(self, race_info: Dict[str, Any]) -> Dict[str, Any]:
        """特定レース分析（同期版）"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # 特定レース用の簡易分析
            result = loop.run_until_complete(self._execute_single_race(race_info))
            loop.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Race analysis error: {str(e)}")
            return self._create_error_response(str(e))

    async def _execute_single_race(self, race_info: Dict[str, Any]) -> Dict[str, Any]:
        """単一レース分析"""
        # 簡略化された分析フロー
        race_data = await self.race_collector.collect_specific_race(race_info)
        if not race_data:
            return self._create_error_response("Race data collection failed")
        
        basic_result = await self._phase_1_basic_analysis(race_data)
        investment = await self.investment_calc.calculate_single_race(basic_result)
        
        return {
            'status': 'success',
            'race_name': race_data.get('race_name', '不明'),
            'analysis': basic_result.details,
            'investment': investment
        }

    def _create_error_result(self, module_name: str, error_msg: str) -> AnalysisResult:
        """エラー結果作成"""
        return AnalysisResult(
            module_name=module_name,
            weight=self.module_weights.get(module_name, 0),
            score=0,
            details={'error': error_msg},
            execution_time=0,
            status='error'
        )

    def _create_success_response(self, evaluation: Dict[str, Any], 
                               investment: Dict[str, Any], 
                               execution_time: float) -> Dict[str, Any]:
        """成功レスポンス作成"""
        return {
            'status': 'success',
            'version': '3.1.0',
            'execution_time': execution_time,
            'predictions': evaluation.get('recommendations', []),
            'investment_strategy': investment,
            'quality_score': evaluation.get('quality_score', 0),
            'timestamp': datetime.now().isoformat()
        }

    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """エラーレスポンス作成"""
        return {
            'status': 'error',
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }
