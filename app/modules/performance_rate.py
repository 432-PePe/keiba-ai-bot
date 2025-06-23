import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """成績指標データクラス"""
    horse_name: str
    overall_win_rate: float
    overall_place_rate: float
    distance_win_rate: float
    distance_place_rate: float
    surface_win_rate: float
    surface_place_rate: float
    class_win_rate: float
    class_place_rate: float
    recent_form_score: float
    consistency_score: float
    performance_score: float

class PerformanceRateAnalysis:
    """連帯率実績分析システム v3.1【15%重み・強化版】"""
    
    def __init__(self):
        self.max_analysis_time = 25  # 秒
        self.weight_in_system = 0.15  # システム全体の15%重み
        
        # 分析重み配分
        self.analysis_weights = {
            'overall_rate': 0.20,      # 全体的な成績
            'distance_rate': 0.25,     # 距離別成績
            'surface_rate': 0.20,      # 馬場別成績
            'class_rate': 0.15,        # クラス別成績
            'recent_form': 0.15,       # 近況
            'consistency': 0.05        # 安定性
        }
        
        # 距離分類
        self.distance_categories = {
            'sprint': (1000, 1400),      # スプリント
            'mile': (1401, 1600),        # マイル
            'middle': (1601, 2000),      # 中距離
            'long': (2001, 3000),        # 長距離
            'steeplechase': (3001, 4000) # 障害
        }
        
        # 成績評価基準
        self.rate_thresholds = {
            'excellent': {'win': 0.25, 'place': 0.60},
            'good': {'win': 0.18, 'place': 0.45},
            'average': {'win': 0.12, 'place': 0.35},
            'poor': {'win': 0.08, 'place': 0.25},
            'very_poor': {'win': 0.00, 'place': 0.00}
        }

    async def analyze(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """連帯率実績分析実行（25秒・15%重み）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting performance rate analysis v3.1")
        
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return self._create_error_result("No horses data")
            
            # レース条件抽出
            race_conditions = self._extract_race_conditions(race_data)
            
            # 各馬の成績分析
            performance_analyses = await self._analyze_all_horses_performance(horses, race_conditions)
            
            # 成績ランキング作成
            performance_ranking = self._create_performance_ranking(performance_analyses)
            
            # 安定性重視馬抽出
            consistent_performers = self._identify_consistent_performers(performance_analyses)
            
            # 条件別優秀馬抽出
            condition_specialists = self._identify_condition_specialists(performance_analyses, race_conditions)
            
            # 近況好調馬分析
            recent_form_analysis = self._analyze_recent_form_trends(performance_analyses)
            
            # 総合成績スコア計算
            overall_score = self._calculate_overall_performance_score(performance_analyses)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Performance rate analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'performance_score': overall_score,
                'horse_performance_analyses': performance_analyses,
                'performance_ranking': performance_ranking,
                'consistent_performers': consistent_performers,
                'condition_specialists': condition_specialists,
                'recent_form_analysis': recent_form_analysis,
                'performance_summary': self._create_performance_summary(
                    performance_analyses, race_conditions
                )
            }
            
        except Exception as e:
            logger.error(f"Performance rate analysis error: {str(e)}")
            return self._create_error_result(str(e))

    async def _analyze_all_horses_performance(self, horses: List[Dict], race_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """全馬成績分析"""
        performance_analyses = []
        
        for horse in horses:
            try:
                analysis = await self._analyze_single_horse_performance(horse, race_conditions)
                if analysis:
                    performance_analyses.append(analysis)
            except Exception as e:
                logger.error(f"Single horse performance analysis error: {str(e)}")
                continue
        
        return performance_analyses

    async def _analyze_single_horse_performance(self, horse: Dict[str, Any], race_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """単一馬成績分析"""
        try:
            horse_name = horse.get('horse_name', '')
            
            # 過去成績データ取得
            past_performances = await self._get_detailed_past_performances(horse)
            
            if not past_performances:
                return self._create_default_performance_analysis(horse_name)
            
            # 全体成績分析
            overall_rates = self._calculate_overall_rates(past_performances)
            
            # 距離別成績分析
            distance_rates = self._calculate_distance_rates(past_performances, race_conditions)
            
            # 馬場別成績分析
            surface_rates = self._calculate_surface_rates(past_performances, race_conditions)
            
            # クラス別成績分析
            class_rates = self._calculate_class_rates(past_performances, race_conditions)
            
            # 近況分析
            recent_form = self._analyze_recent_form(past_performances)
            
            # 安定性分析
            consistency = self._analyze_consistency(past_performances)
            
            # 特殊条件成績
            special_conditions = self._analyze_special_conditions(past_performances, race_conditions)
            
            # 総合成績スコア計算
            performance_score = self._calculate_horse_performance_score(
                overall_rates, distance_rates, surface_rates, class_rates, recent_form, consistency
            )
            
            return {
                'horse_name': horse_name,
                'overall_rates': overall_rates,
                'distance_rates': distance_rates,
                'surface_rates': surface_rates,
                'class_rates': class_rates,
                'recent_form': recent_form,
                'consistency': consistency,
                'special_conditions': special_conditions,
                'performance_score': performance_score,
                'performance_rating': self._score_to_rating(performance_score),
                'performance_strengths': self._identify_performance_strengths(
                    overall_rates, distance_rates, surface_rates, class_rates
                ),
                'reliability_assessment': self._assess_reliability(consistency, overall_rates)
            }
            
        except Exception as e:
            logger.error(f"Single horse performance analysis error: {str(e)}")
            return self._create_default_performance_analysis(horse.get('horse_name', ''))

    async def _get_detailed_past_performances(self, horse: Dict[str, Any]) -> List[Dict[str, Any]]:
        """詳細過去成績取得"""
        try:
            # 実際の実装では外部APIやデータベースから詳細成績を取得
            # ここでは模擬データを使用
            
            horse_name = horse.get('horse_name', '')
            
            # 模擬詳細成績データ（より充実）
            past_performances = []
            for i in range(12):  # 過去12走
                performance = {
                    'race_date': (datetime.now() - timedelta(days=45*(i+1))).strftime('%Y-%m-%d'),
                    'race_name': f'過去レース{i+1}',
                    'finish_position': min(18, max(1, 4 + (i % 8))),
                    'horse_count': 14 + (i % 4),
                    'distance': 1200 + (i % 6) * 200,
                    'surface': '芝' if i % 3 != 0 else 'ダート',
                    'track': ['中山', '東京', '京都', '阪神'][i % 4],
                    'race_class': self._generate_race_class(i),
                    'weight_carried': 54.0 + (i % 4),
                    'jockey': f'騎手{(i % 5) + 1}',
                    'odds': 3.0 + (i % 10),
                    'margin': f"{(i % 10) * 0.3}",
                    'pace': ['S', 'M', 'H'][i % 3],
                    'weather': ['晴', '曇', '雨'][i % 3],
                    'track_condition': ['良', '稍重', '重'][i % 3],
                    'running_style': ['逃げ', '先行', '差し', '追込'][i % 4],
                    'prize_money': max(0, 500 - i * 30),  # 万円
                    'time': f"1:{35 + (i % 5)}:{20 + (i % 6)}",
                    'last_3f': f"{34 + (i % 4)}.{i % 10}"
                }
                past_performances.append(performance)
            
            return past_performances
            
        except Exception as e:
            logger.error(f"Detailed past performances retrieval error: {str(e)}")
            return []

    def _calculate_overall_rates(self, past_performances: List[Dict]) -> Dict[str, Any]:
        """全体成績計算"""
        try:
            if not past_performances:
                return {'win_rate': 0.0, 'place_rate': 0.0, 'total_races': 0}
            
            total_races = len(past_performances)
            wins = sum(1 for p in past_performances if p.get('finish_position', 99) == 1)
            places = sum(1 for p in past_performances if p.get('finish_position', 99) <= 3)
            
            win_rate = wins / total_races if total_races > 0 else 0.0
            place_rate = places / total_races if total_races > 0 else 0.0
            
            # 平均着順
            avg_finish = statistics.mean([p.get('finish_position', 10) for p in past_performances])
            
            # 賞金総額
            total_prize = sum([p.get('prize_money', 0) for p in past_performances])
            
            return {
                'win_rate': win_rate,
                'place_rate': place_rate,
                'total_races': total_races,
                'wins': wins,
                'places': places,
                'average_finish': avg_finish,
                'total_prize_money': total_prize,
                'rate_rating': self._rate_to_rating(win_rate, place_rate)
            }
            
        except Exception as e:
            logger.error(f"Overall rates calculation error: {str(e)}")
            return {'win_rate': 0.0, 'place_rate': 0.0, 'total_races': 0}

    def _calculate_distance_rates(self, past_performances: List[Dict], race_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """距離別成績計算"""
        try:
            target_distance = race_conditions.get('distance', 1600)
            target_category = self._categorize_distance(target_distance)
            
            # 同距離帯成績
            same_category_performances = [
                p for p in past_performances 
                if self._categorize_distance(p.get('distance', 1600)) == target_category
            ]
            
            if same_category_performances:
                same_category_stats = self._calculate_category_stats(same_category_performances)
            else:
                same_category_stats = {'win_rate': 0.0, 'place_rate': 0.0, 'races': 0}
            
            # 距離別統計
            distance_stats = {}
            for category, (min_dist, max_dist) in self.distance_categories.items():
                category_performances = [
                    p for p in past_performances 
                    if min_dist <= p.get('distance', 1600) <= max_dist
                ]
                if category_performances:
                    distance_stats[category] = self._calculate_category_stats(category_performances)
                else:
                    distance_stats[category] = {'win_rate': 0.0, 'place_rate': 0.0, 'races': 0}
            
            # 距離適性評価
            distance_aptitude = self._evaluate_distance_aptitude(distance_stats, target_category)
            
            return {
                'target_distance': target_distance,
                'target_category': target_category,
                'same_category_stats': same_category_stats,
                'distance_stats': distance_stats,
                'distance_aptitude': distance_aptitude,
                'distance_score': same_category_stats.get('place_rate', 0.0) * 100
            }
            
        except Exception as e:
            logger.error(f"Distance rates calculation error: {str(e)}")
            return {'distance_score': 0.0, 'target_category': 'middle'}

    def _calculate_surface_rates(self, past_performances: List[Dict], race_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """馬場別成績計算"""
        try:
            target_surface = race_conditions.get('surface', '芝')
            
            # 芝成績
            turf_performances = [p for p in past_performances if p.get('surface') == '芝']
            turf_stats = self._calculate_category_stats(turf_performances) if turf_performances else {'win_rate': 0.0, 'place_rate': 0.0, 'races': 0}
            
            # ダート成績
            dirt_performances = [p for p in past_performances if p.get('surface') == 'ダート']
            dirt_stats = self._calculate_category_stats(dirt_performances) if dirt_performances else {'win_rate': 0.0, 'place_rate': 0.0, 'races': 0}
            
            # 対象馬場の成績
            target_surface_stats = turf_stats if target_surface == '芝' else dirt_stats
            
            # 馬場適性評価
            surface_preference = self._evaluate_surface_preference(turf_stats, dirt_stats)
            
            return {
                'target_surface': target_surface,
                'turf_stats': turf_stats,
                'dirt_stats': dirt_stats,
                'target_surface_stats': target_surface_stats,
                'surface_preference': surface_preference,
                'surface_score': target_surface_stats.get('place_rate', 0.0) * 100
            }
            
        except Exception as e:
            logger.error(f"Surface rates calculation error: {str(e)}")
            return {'surface_score': 0.0, 'target_surface': '芝'}

    def _calculate_class_rates(self, past_performances: List[Dict], race_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """クラス別成績計算"""
        try:
            target_class = race_conditions.get('race_class', 'OP')
            
            # クラス別統計
            class_stats = {}
            class_levels = ['G1', 'G2', 'G3', 'OP', '3勝', '2勝', '1勝', 'maiden']
            
            for class_level in class_levels:
                class_performances = [
                    p for p in past_performances 
                    if p.get('race_class', '') == class_level
                ]
                if class_performances:
                    class_stats[class_level] = self._calculate_category_stats(class_performances)
                else:
                    class_stats[class_level] = {'win_rate': 0.0, 'place_rate': 0.0, 'races': 0}
            
            # 対象クラス成績
            target_class_stats = class_stats.get(target_class, {'win_rate': 0.0, 'place_rate': 0.0, 'races': 0})
            
            # 格上挑戦・格下げ分析
            class_trend = self._analyze_class_trend(past_performances)
            
            return {
                'target_class': target_class,
                'class_stats': class_stats,
                'target_class_stats': target_class_stats,
                'class_trend': class_trend,
                'class_score': target_class_stats.get('place_rate', 0.0) * 100
            }
            
        except Exception as e:
            logger.error(f"Class rates calculation error: {str(e)}")
            return {'class_score': 0.0, 'target_class': 'OP'}

    def _analyze_recent_form(self, past_performances: List[Dict]) -> Dict[str, Any]:
        """近況分析"""
        try:
            if not past_performances:
                return {'recent_score': 0.0, 'form_trend': 'unknown'}
            
            # 直近3走分析
            recent_3 = past_performances[:3]
            recent_3_score = self._calculate_recent_score(recent_3)
            
            # 直近5走分析
            recent_5 = past_performances[:5]
            recent_5_score = self._calculate_recent_score(recent_5)
            
            # フォームトレンド分析
            form_trend = self._analyze_form_trend(past_performances[:6])
            
            # 休み明け分析
            layoff_analysis = self._analyze_layoff_performance(past_performances)
            
            # 総合近況スコア
            recent_score = (recent_3_score * 0.6 + recent_5_score * 0.4)
            
            return {
                'recent_score': recent_score,
                'recent_3_score': recent_3_score,
                'recent_5_score': recent_5_score,
                'form_trend': form_trend,
                'layoff_analysis': layoff_analysis,
                'recent_rating': self._score_to_rating(recent_score)
            }
            
        except Exception as e:
            logger.error(f"Recent form analysis error: {str(e)}")
            return {'recent_score': 50.0, 'form_trend': 'stable'}

    def _analyze_consistency(self, past_performances: List[Dict]) -> Dict[str, Any]:
        """安定性分析"""
        try:
            if len(past_performances) < 3:
                return {'consistency_score': 0.0, 'stability_rating': 'insufficient_data'}
            
            # 着順の標準偏差
            positions = [p.get('finish_position', 10) for p in past_performances[:8]]
            position_std = statistics.stdev(positions) if len(positions) > 1 else 0
            
            # 連続好走分析
            consecutive_good_runs = self._analyze_consecutive_runs(past_performances)
            
            # 大敗率分析
            big_defeats = self._analyze_big_defeats(past_performances)
            
            # 安定性スコア計算
            consistency_score = max(0, 100 - (position_std * 10) - (big_defeats['rate'] * 50))
            
            return {
                'consistency_score': consistency_score,
                'position_std': position_std,
                'consecutive_good_runs': consecutive_good_runs,
                'big_defeats': big_defeats,
                'stability_rating': self._score_to_rating(consistency_score)
            }
            
        except Exception as e:
            logger.error(f"Consistency analysis error: {str(e)}")
            return {'consistency_score': 50.0, 'stability_rating': 'average'}

    def _calculate_horse_performance_score(self, overall_rates: Dict, distance_rates: Dict, 
                                         surface_rates: Dict, class_rates: Dict, 
                                         recent_form: Dict, consistency: Dict) -> float:
        """馬の成績総合スコア計算"""
        try:
            overall_score = overall_rates.get('place_rate', 0.0) * 100
            distance_score = distance_rates.get('distance_score', 0.0)
            surface_score = surface_rates.get('surface_score', 0.0)
            class_score = class_rates.get('class_score', 0.0)
            recent_score = recent_form.get('recent_score', 0.0)
            consistency_score = consistency.get('consistency_score', 0.0)
            
            # 重み付き計算
            total_score = (
                overall_score * self.analysis_weights['overall_rate'] +
                distance_score * self.analysis_weights['distance_rate'] +
                surface_score * self.analysis_weights['surface_rate'] +
                class_score * self.analysis_weights['class_rate'] +
                recent_score * self.analysis_weights['recent_form'] +
                consistency_score * self.analysis_weights['consistency']
            )
            
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"Horse performance score calculation error: {str(e)}")
            return 50.0

    # ヘルパーメソッド
    def _categorize_distance(self, distance: int) -> str:
        """距離カテゴリ分類"""
        for category, (min_dist, max_dist) in self.distance_categories.items():
            if min_dist <= distance <= max_dist:
                return category
        return 'middle'  # デフォルト

    def _calculate_category_stats(self, performances: List[Dict]) -> Dict[str, Any]:
        """カテゴリ統計計算"""
        if not performances:
            return {'win_rate': 0.0, 'place_rate': 0.0, 'races': 0}
        
        races = len(performances)
        wins = sum(1 for p in performances if p.get('finish_position', 99) == 1)
        places = sum(1 for p in performances if p.get('finish_position', 99) <= 3)
        
        return {
            'win_rate': wins / races,
            'place_rate': places / races,
            'races': races,
            'wins': wins,
            'places': places
        }

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

    def _rate_to_rating(self, win_rate: float, place_rate: float) -> str:
        """勝率・連対率を評価に変換"""
        if win_rate >= 0.25 or place_rate >= 0.60:
            return 'excellent'
        elif win_rate >= 0.18 or place_rate >= 0.45:
            return 'good'
        elif win_rate >= 0.12 or place_rate >= 0.35:
            return 'average'
        elif win_rate >= 0.08 or place_rate >= 0.25:
            return 'poor'
        else:
            return 'very_poor'

    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """エラー結果作成"""
        return {
            'status': 'error',
            'error_message': error_msg,
            'performance_score': 0,
            'execution_time': 0
        }

    # ... その他のヘルパーメソッドは実装省略（実際の開発時に詳細実装）
