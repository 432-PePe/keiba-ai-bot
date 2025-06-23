import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JockeyTrainerCompatibility:
    """騎手厩舎相性データ"""
    jockey_name: str
    trainer_name: str
    combination_win_rate: float
    combination_place_rate: float
    total_races: int
    recent_form: str
    distance_specialty: Dict[str, float]
    surface_specialty: Dict[str, float]
    compatibility_score: float

class JockeyTrainerAnalysis:
    """騎手厩舎相性分析システム v3.1【22%重み・強化版】"""
    
    def __init__(self):
        self.max_analysis_time = 40  # 秒
        self.weight_in_system = 0.22  # システム全体の22%重み（最高重み）
        
        # 分析重み配分
        self.analysis_weights = {
            'combination_history': 0.35,    # コンビ実績
            'individual_performance': 0.25, # 個別成績
            'recent_form': 0.20,           # 近況
            'distance_surface_fit': 0.20   # 距離・馬場適性
        }
        
        # 評価基準
        self.win_rate_thresholds = {
            'excellent': 0.25,  # 25%以上
            'good': 0.18,       # 18%以上
            'average': 0.12,    # 12%以上
            'poor': 0.08,       # 8%以上
            'very_poor': 0.0    # 8%未満
        }

    async def analyze(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """騎手厩舎相性分析実行（40秒・22%重み）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting jockey-trainer compatibility analysis v3.1")
        
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return self._create_error_result("No horses data")
            
            # 並行処理で各馬の騎手厩舎分析
            compatibility_analyses = await self._analyze_all_combinations(horses, race_data)
            
            # 相性ランキング作成
            compatibility_ranking = self._create_compatibility_ranking(compatibility_analyses)
            
            # 特別注目コンビ抽出
            special_combinations = self._identify_special_combinations(compatibility_analyses)
            
            # 厩舎別・騎手別統計
            stable_stats = self._calculate_stable_statistics(compatibility_analyses)
            jockey_stats = self._calculate_jockey_statistics(compatibility_analyses)
            
            # 総合評価スコア計算
            overall_score = self._calculate_overall_compatibility_score(compatibility_analyses)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Jockey-trainer analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'compatibility_score': overall_score,
                'horse_compatibility_analyses': compatibility_analyses,
                'compatibility_ranking': compatibility_ranking,
                'special_combinations': special_combinations,
                'stable_statistics': stable_stats,
                'jockey_statistics': jockey_stats,
                'analysis_summary': self._create_analysis_summary(compatibility_analyses)
            }
            
        except Exception as e:
            logger.error(f"Jockey-trainer analysis error: {str(e)}")
            return self._create_error_result(str(e))

    async def _analyze_all_combinations(self, horses: List[Dict], race_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """全馬の騎手厩舎組み合わせ分析"""
        tasks = []
        
        for horse in horses:
            task = self._analyze_single_combination(horse, race_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Single combination analysis error: {result}")
                continue
            if result:
                valid_results.append(result)
        
        return valid_results

    async def _analyze_single_combination(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """単一馬の騎手厩舎相性分析"""
        try:
            horse_name = horse.get('horse_name', '')
            jockey_name = horse.get('jockey', '')
            trainer_name = horse.get('trainer', '')
            
            if not jockey_name or not trainer_name:
                return self._create_minimal_analysis(horse_name, jockey_name, trainer_name)
            
            # コンビ実績分析（35%重み）
            combination_history = await self._analyze_combination_history(jockey_name, trainer_name)
            
            # 個別成績分析（25%重み）
            individual_performance = await self._analyze_individual_performance(
                jockey_name, trainer_name, race_data
            )
            
            # 近況分析（20%重み）
            recent_form = await self._analyze_recent_form(jockey_name, trainer_name)
            
            # 距離・馬場適性分析（20%重み）
            distance_surface_fit = await self._analyze_distance_surface_fitness(
                jockey_name, trainer_name, race_data
            )
            
            # 重み付き総合スコア計算
            compatibility_score = self._calculate_compatibility_score(
                combination_history, individual_performance, recent_form, distance_surface_fit
            )
            
            return {
                'horse_name': horse_name,
                'jockey_name': jockey_name,
                'trainer_name': trainer_name,
                'combination_history': combination_history,
                'individual_performance': individual_performance,
                'recent_form': recent_form,
                'distance_surface_fit': distance_surface_fit,
                'compatibility_score': compatibility_score,
                'compatibility_rating': self._score_to_rating(compatibility_score),
                'recommendation': self._generate_recommendation(compatibility_score)
            }
            
        except Exception as e:
            logger.error(f"Single combination analysis error: {str(e)}")
            return self._create_minimal_analysis(
                horse.get('horse_name', ''), 
                horse.get('jockey', ''), 
                horse.get('trainer', '')
            )

    async def _analyze_combination_history(self, jockey_name: str, trainer_name: str) -> Dict[str, Any]:
        """コンビ実績分析（35%重み）"""
        try:
            # 実際の実装ではデータベースやAPIから取得
            # ここでは模擬データで実装
            
            # 過去のコンビ成績を分析
            combination_stats = {
                'total_races': 0,
                'wins': 0,
                'places': 0,
                'win_rate': 0.0,
                'place_rate': 0.0,
                'recent_races': [],
                'best_performances': []
            }
            
            # 模擬的な実績計算（実際はデータベースクエリ）
            if self._is_established_combination(jockey_name, trainer_name):
                combination_stats.update({
                    'total_races': 25,
                    'wins': 5,
                    'places': 12,
                    'win_rate': 0.20,
                    'place_rate': 0.48
                })
            else:
                # 新コンビや稀なコンビの場合
                combination_stats.update({
                    'total_races': 3,
                    'wins': 0,
                    'places': 1,
                    'win_rate': 0.0,
                    'place_rate': 0.33
                })
            
            # コンビ実績スコア計算
            history_score = self._calculate_history_score(combination_stats)
            
            return {
                'combination_stats': combination_stats,
                'history_score': history_score,
                'combination_type': self._classify_combination_type(combination_stats),
                'reliability': self._assess_data_reliability(combination_stats['total_races'])
            }
            
        except Exception as e:
            logger.error(f"Combination history analysis error: {str(e)}")
            return {'history_score': 50.0, 'combination_type': 'unknown'}

    async def _analyze_individual_performance(self, jockey_name: str, trainer_name: str, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """個別成績分析（25%重み）"""
        try:
            # 騎手個別成績
            jockey_performance = await self._get_jockey_performance(jockey_name, race_data)
            
            # 厩舎個別成績
            trainer_performance = await self._get_trainer_performance(trainer_name, race_data)
            
            # 個別成績統合スコア
            individual_score = (jockey_performance['score'] * 0.6 + 
                              trainer_performance['score'] * 0.4)
            
            return {
                'jockey_performance': jockey_performance,
                'trainer_performance': trainer_performance,
                'individual_score': individual_score,
                'strength_analysis': self._analyze_individual_strengths(
                    jockey_performance, trainer_performance
                )
            }
            
        except Exception as e:
            logger.error(f"Individual performance analysis error: {str(e)}")
            return {'individual_score': 50.0}

    async def _get_jockey_performance(self, jockey_name: str, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """騎手成績取得・分析"""
        try:
            # 模擬データ（実際はデータベースから取得）
            performance_data = {
                'recent_win_rate': 0.15,  # 直近勝率
                'recent_place_rate': 0.45,  # 直近連対率
                'total_races_this_year': 180,
                'wins_this_year': 27,
                'places_this_year': 81,
                'grade_race_experience': True,
                'distance_specialty': self._get_jockey_distance_specialty(jockey_name),
                'surface_specialty': self._get_jockey_surface_specialty(jockey_name)
            }
            
            # 騎手スコア計算
            jockey_score = self._calculate_jockey_score(performance_data)
            
            return {
                'performance_data': performance_data,
                'score': jockey_score,
                'rating': self._score_to_rating(jockey_score),
                'specialties': {
                    'distance': performance_data['distance_specialty'],
                    'surface': performance_data['surface_specialty']
                }
            }
            
        except Exception as e:
            logger.error(f"Jockey performance error: {str(e)}")
            return {'score': 50.0, 'rating': 'average'}

    async def _get_trainer_performance(self, trainer_name: str, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """厩舎成績取得・分析"""
        try:
            # 模擬データ（実際はデータベースから取得）
            performance_data = {
                'recent_win_rate': 0.12,
                'recent_place_rate': 0.38,
                'total_horses_this_year': 45,
                'wins_this_year': 8,
                'stable_form': 'good',  # good, average, poor
                'specialty_analysis': self._get_trainer_specialty(trainer_name)
            }
            
            # 厩舎スコア計算
            trainer_score = self._calculate_trainer_score(performance_data)
            
            return {
                'performance_data': performance_data,
                'score': trainer_score,
                'rating': self._score_to_rating(trainer_score),
                'stable_characteristics': performance_data['specialty_analysis']
            }
            
        except Exception as e:
            logger.error(f"Trainer performance error: {str(e)}")
            return {'score': 50.0, 'rating': 'average'}

    def _calculate_compatibility_score(self, combination_history: Dict, individual_performance: Dict, 
                                     recent_form: Dict, distance_surface_fit: Dict) -> float:
        """相性スコア計算"""
        try:
            history_score = combination_history.get('history_score', 50.0)
            individual_score = individual_performance.get('individual_score', 50.0)
            form_score = recent_form.get('form_score', 50.0)
            fit_score = distance_surface_fit.get('fit_score', 50.0)
            
            # 重み付き計算
            total_score = (
                history_score * self.analysis_weights['combination_history'] +
                individual_score * self.analysis_weights['individual_performance'] +
                form_score * self.analysis_weights['recent_form'] +
                fit_score * self.analysis_weights['distance_surface_fit']
            )
            
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"Compatibility score calculation error: {str(e)}")
            return 50.0

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
            'compatibility_score': 0,
            'execution_time': 0
        }

    # その他のヘルパーメソッド（実装省略）
    def _is_established_combination(self, jockey: str, trainer: str) -> bool:
        """確立されたコンビかどうか判定"""
        return True  # 簡略化

    def _calculate_history_score(self, stats: Dict) -> float:
        """実績スコア計算"""
        if stats['total_races'] == 0:
            return 50.0
        
        win_rate = stats['win_rate']
        place_rate = stats['place_rate']
        
        score = (win_rate * 60 + place_rate * 40) * 100
        return max(0, min(100, score))

    # ... その他のメソッドは実装省略（実際の開発時に詳細実装）
