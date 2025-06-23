import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PreRaceInfo:
    """直前情報データクラス"""
    horse_name: str
    paddock_evaluation: str
    weight_change: float
    jockey_change: bool
    equipment_change: bool
    weather_impact: str
    track_condition_impact: str
    late_scratches: bool
    betting_move: str
    pre_race_score: float

class PreRaceInfoAnalysis:
    """直前情報分析システム v3.1【3%重み・最終調整】"""
    
    def __init__(self):
        self.max_analysis_time = 5  # 秒
        self.weight_in_system = 0.03  # システム全体の3%重み
        
        # 直前情報の重み配分
        self.analysis_weights = {
            'paddock_evaluation': 0.30,   # パドック評価
            'weight_changes': 0.20,       # 馬体重変動
            'last_minute_changes': 0.20,  # 直前変更
            'weather_track': 0.15,        # 天候・馬場
            'betting_moves': 0.15         # 投票動向
        }
        
        # パドック評価基準
        self.paddock_ratings = {
            'excellent': {'score': 90, 'description': '非常に良い状態'},
            'good': {'score': 75, 'description': '良好な状態'},
            'average': {'score': 60, 'description': '普通の状態'},
            'poor': {'score': 40, 'description': 'やや不安な状態'},
            'very_poor': {'score': 20, 'description': '明らかに不調'}
        }
        
        # 馬体重変動の評価
        self.weight_change_impact = {
            'significant_increase': (-15, '大幅増加（不安要素）'),
            'moderate_increase': (-8, '増加（やや不安）'),
            'ideal_increase': (5, '理想的増加'),
            'stable': (0, '安定'),
            'moderate_decrease': (-5, '減少（やや不安）'),
            'significant_decrease': (-20, '大幅減少（警戒）')
        }

    async def analyze(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """直前情報分析実行（5秒・3%重み）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting pre-race info analysis v3.1")
        
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return self._create_error_result("No horses data")
            
            # 直前レース条件取得
            current_conditions = self._get_current_race_conditions(race_data)
            
            # 各馬の直前情報分析
            pre_race_analyses = await self._analyze_all_horses_pre_race(horses, current_conditions)
            
            # 直前注目馬抽出
            notable_pre_race_factors = self._identify_notable_pre_race_factors(pre_race_analyses)
            
            # 直前リスク馬特定
            pre_race_risks = self._identify_pre_race_risks(pre_race_analyses)
            
            # 天候・馬場影響分析
            weather_track_impact = self._analyze_weather_track_impact(current_conditions, pre_race_analyses)
            
            # 直前投票動向分析
            late_betting_trends = self._analyze_late_betting_trends(pre_race_analyses)
            
            # 総合直前情報スコア
            overall_score = self._calculate_overall_pre_race_score(pre_race_analyses)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Pre-race info analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'pre_race_score': overall_score,
                'horse_pre_race_analyses': pre_race_analyses,
                'notable_pre_race_factors': notable_pre_race_factors,
                'pre_race_risks': pre_race_risks,
                'weather_track_impact': weather_track_impact,
                'late_betting_trends': late_betting_trends,
                'pre_race_summary': self._create_pre_race_summary(
                    pre_race_analyses, notable_pre_race_factors, pre_race_risks
                )
            }
            
        except Exception as e:
            logger.error(f"Pre-race info analysis error: {str(e)}")
            return self._create_error_result(str(e))

    async def _analyze_all_horses_pre_race(self, horses: List[Dict], current_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """全馬直前情報分析"""
        pre_race_analyses = []
        
        for horse in horses:
            try:
                analysis = await self._analyze_single_horse_pre_race(horse, current_conditions)
                if analysis:
                    pre_race_analyses.append(analysis)
            except Exception as e:
                logger.error(f"Single horse pre-race analysis error: {str(e)}")
                continue
        
        return pre_race_analyses

    async def _analyze_single_horse_pre_race(self, horse: Dict[str, Any], current_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """単一馬直前情報分析"""
        try:
            horse_name = horse.get('horse_name', '')
            
            # パドック情報取得・評価
            paddock_evaluation = await self._evaluate_paddock_condition(horse)
            
            # 馬体重変動分析
            weight_analysis = await self._analyze_weight_changes(horse)
            
            # 直前変更分析
            last_minute_changes = await self._analyze_last_minute_changes(horse)
            
            # 天候・馬場影響分析
            weather_track_analysis = self._analyze_weather_track_impact_single(horse, current_conditions)
            
            # 投票動向分析
            betting_move_analysis = await self._analyze_betting_moves(horse)
            
            # 直前総合スコア計算
            pre_race_score = self._calculate_horse_pre_race_score(
                paddock_evaluation, weight_analysis, last_minute_changes,
                weather_track_analysis, betting_move_analysis
            )
            
            # 直前推奨度判定
            pre_race_recommendation = self._determine_pre_race_recommendation(
                pre_race_score, paddock_evaluation, weight_analysis, last_minute_changes
            )
            
            return {
                'horse_name': horse_name,
                'paddock_evaluation': paddock_evaluation,
                'weight_analysis': weight_analysis,
                'last_minute_changes': last_minute_changes,
                'weather_track_analysis': weather_track_analysis,
                'betting_move_analysis': betting_move_analysis,
                'pre_race_score': pre_race_score,
                'pre_race_rating': self._score_to_rating(pre_race_score),
                'pre_race_recommendation': pre_race_recommendation,
                'key_pre_race_factors': self._extract_key_pre_race_factors(
                    paddock_evaluation, weight_analysis, last_minute_changes
                )
            }
            
        except Exception as e:
            logger.error(f"Single horse pre-race analysis error: {str(e)}")
            return None

    async def _evaluate_paddock_condition(self, horse: Dict[str, Any]) -> Dict[str, Any]:
        """パドック状態評価"""
        try:
            # 実際の実装では画像解析やエキスパート評価を取得
            # ここでは模擬データを使用
            
            horse_name = horse.get('horse_name', '')
            
            # 模擬パドック評価（実際は専門家の評価やAI画像解析）
            import random
            random.seed(hash(horse_name) % 1000)  # 一貫性のため
            
            # パドック評価要素
            coat_condition = random.choice(['excellent', 'good', 'average', 'poor'])
            walking_gait = random.choice(['smooth', 'normal', 'slightly_stiff', 'concerning'])
            alertness = random.choice(['very_alert', 'alert', 'calm', 'dull'])
            muscle_tone = random.choice(['excellent', 'good', 'average', 'soft'])
            
            # 総合パドック評価
            evaluation_scores = {
                'coat_condition': self._evaluate_coat_condition(coat_condition),
                'walking_gait': self._evaluate_walking_gait(walking_gait),
                'alertness': self._evaluate_alertness(alertness),
                'muscle_tone': self._evaluate_muscle_tone(muscle_tone)
            }
            
            # 総合スコア計算
            total_score = (
                evaluation_scores['coat_condition'] * 0.3 +
                evaluation_scores['walking_gait'] * 0.3 +
                evaluation_scores['alertness'] * 0.2 +
                evaluation_scores['muscle_tone'] * 0.2
            )
            
            # 総合評価判定
            if total_score >= 85:
                overall_evaluation = 'excellent'
            elif total_score >= 70:
                overall_evaluation = 'good'
            elif total_score >= 55:
                overall_evaluation = 'average'
            elif total_score >= 40:
                overall_evaluation = 'poor'
            else:
                overall_evaluation = 'very_poor'
            
            return {
                'overall_evaluation': overall_evaluation,
                'total_score': total_score,
                'coat_condition': coat_condition,
                'walking_gait': walking_gait,
                'alertness': alertness,
                'muscle_tone': muscle_tone,
                'evaluation_scores': evaluation_scores,
                'paddock_notes': self._generate_paddock_notes(overall_evaluation, coat_condition, walking_gait)
            }
            
        except Exception as e:
            logger.error(f"Paddock evaluation error: {str(e)}")
            return {'overall_evaluation': 'average', 'total_score': 60.0}

    async def _analyze_weight_changes(self, horse: Dict[str, Any]) -> Dict[str, Any]:
        """馬体重変動分析"""
        try:
            # 実際の実装では前走からの体重変化を取得
            # ここでは模擬データを使用
            
            current_weight = horse.get('weight', 480)  # 現在の体重
            
            # 前走体重（模擬）
            import random
            horse_name = horse.get('horse_name', '')
            random.seed(hash(horse_name + 'weight') % 1000)
            
            previous_weight = current_weight + random.randint(-20, 15)
            weight_change = current_weight - previous_weight
            
            # 体重変動の評価
            weight_change_evaluation = self._evaluate_weight_change(weight_change)
            
            # 体重による影響度
            weight_impact_score = self._calculate_weight_impact_score(weight_change, current_weight)
            
            return {
                'current_weight': current_weight,
                'previous_weight': previous_weight,
                'weight_change': weight_change,
                'weight_change_evaluation': weight_change_evaluation,
                'weight_impact_score': weight_impact_score,
                'weight_trend': 'increasing' if weight_change > 0 else 'decreasing' if weight_change < 0 else 'stable',
                'weight_concern_level': self._assess_weight_concern_level(weight_change)
            }
            
        except Exception as e:
            logger.error(f"Weight analysis error: {str(e)}")
            return {'weight_impact_score': 60.0, 'weight_change': 0}

    async def _analyze_last_minute_changes(self, horse: Dict[str, Any]) -> Dict[str, Any]:
        """直前変更分析"""
        try:
            # 実際の実装では公式発表から直前変更を取得
            # ここでは模擬データを使用
            
            horse_name = horse.get('horse_name', '')
            
            # 模擬直前変更情報
            import random
            random.seed(hash(horse_name + 'changes') % 1000)
            
            # 各種変更の可能性
            jockey_change = random.random() < 0.05  # 5%の確率で騎手変更
            equipment_change = random.random() < 0.10  # 10%の確率で装具変更
            late_scratch = random.random() < 0.02  # 2%の確率で出走取消
            
            changes = []
            change_impact_score = 60.0  # ベーススコア
            
            if jockey_change:
                changes.append('騎手変更')
                change_impact_score -= 15  # 騎手変更は大きなマイナス
            
            if equipment_change:
                equipment_type = random.choice(['ブリンカー装着', 'ブリンカー外し', 'メンコ装着', 'バンデージ変更'])
                changes.append(equipment_type)
                
                # 装具変更の影響
                if '装着' in equipment_type:
                    change_impact_score += 10  # 装着は集中力向上の可能性
                else:
                    change_impact_score += 5   # 外しも良い場合がある
            
            if late_scratch:
                changes.append('出走取消')
                change_impact_score = 0  # 出走取消は分析対象外
            
            return {
                'has_changes': len(changes) > 0,
                'changes': changes,
                'jockey_change': jockey_change,
                'equipment_change': equipment_change,
                'late_scratch': late_scratch,
                'change_impact_score': change_impact_score,
                'change_assessment': self._assess_change_impact(changes, change_impact_score)
            }
            
        except Exception as e:
            logger.error(f"Last minute changes analysis error: {str(e)}")
            return {'change_impact_score': 60.0, 'has_changes': False}

    def _analyze_weather_track_impact_single(self, horse: Dict[str, Any], current_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """天候・馬場影響分析（単一馬）"""
        try:
            weather = current_conditions.get('weather', '晴')
            track_condition = current_conditions.get('track_condition', '良')
            
            # 天候適性評価（過去成績ベース）
            weather_aptitude = self._evaluate_weather_aptitude(horse, weather)
            
            # 馬場状態適性評価
            track_aptitude = self._evaluate_track_condition_aptitude(horse, track_condition)
            
            # 総合天候・馬場スコア
            weather_track_score = (weather_aptitude * 0.4 + track_aptitude * 0.6)
            
            return {
                'weather': weather,
                'track_condition': track_condition,
                'weather_aptitude': weather_aptitude,
                'track_aptitude': track_aptitude,
                'weather_track_score': weather_track_score,
                'condition_impact': self._assess_condition_impact(weather_track_score)
            }
            
        except Exception as e:
            logger.error(f"Weather track impact analysis error: {str(e)}")
            return {'weather_track_score': 60.0, 'condition_impact': 'neutral'}

    async def _analyze_betting_moves(self, horse: Dict[str, Any]) -> Dict[str, Any]:
        """投票動向分析"""
        try:
            # 実際の実装ではリアルタイムオッズ変動を取得
            # ここでは模擬データを使用
            
            horse_name = horse.get('horse_name', '')
            current_odds = float(horse.get('odds', 10.0))
            
            # 模擬オッズ変動
            import random
            random.seed(hash(horse_name + 'betting') % 1000)
            
            opening_odds = current_odds * (0.8 + random.random() * 0.4)  # ±20%の変動
            odds_movement = current_odds - opening_odds
            
            # 投票動向の評価
            if odds_movement < -1.0:
                betting_trend = 'strong_support'    # 強い支持
                trend_score = 80
            elif odds_movement < -0.3:
                betting_trend = 'moderate_support'  # 中程度の支持
                trend_score = 70
            elif odds_movement > 1.0:
                betting_trend = 'weak_support'      # 弱い支持
                trend_score = 40
            else:
                betting_trend = 'stable'            # 安定
                trend_score = 60
            
            return {
                'opening_odds': opening_odds,
                'current_odds': current_odds,
                'odds_movement': odds_movement,
                'betting_trend': betting_trend,
                'trend_score': trend_score,
                'market_confidence': self._assess_market_confidence(betting_trend, odds_movement)
            }
            
        except Exception as e:
            logger.error(f"Betting moves analysis error: {str(e)}")
            return {'trend_score': 60.0, 'betting_trend': 'stable'}

    def _calculate_horse_pre_race_score(self, paddock_evaluation: Dict, weight_analysis: Dict, 
                                      last_minute_changes: Dict, weather_track_analysis: Dict, 
                                      betting_move_analysis: Dict) -> float:
        """馬の直前情報総合スコア計算"""
        try:
            paddock_score = paddock_evaluation.get('total_score', 60.0)
            weight_score = weight_analysis.get('weight_impact_score', 60.0)
            change_score = last_minute_changes.get('change_impact_score', 60.0)
            weather_score = weather_track_analysis.get('weather_track_score', 60.0)
            betting_score = betting_move_analysis.get('trend_score', 60.0)
            
            # 重み付き計算
            total_score = (
                paddock_score * self.analysis_weights['paddock_evaluation'] +
                weight_score * self.analysis_weights['weight_changes'] +
                change_score * self.analysis_weights['last_minute_changes'] +
                weather_score * self.analysis_weights['weather_track'] +
                betting_score * self.analysis_weights['betting_moves']
            )
            
            return max(0, min(100, total_score))
            
        except Exception as e:
            logger.error(f"Horse pre-race score calculation error: {str(e)}")
            return 60.0

    def _identify_notable_pre_race_factors(self, pre_race_analyses: List[Dict]) -> List[Dict]:
        """直前注目要因特定"""
        try:
            notable_factors = []
            
            for analysis in pre_race_analyses:
                horse_name = analysis.get('horse_name', '')
                pre_race_score = analysis.get('pre_race_score', 60.0)
                
                # 注目要因の条件
                if pre_race_score >= 80:
                    factor_type = 'positive_highlight'
                    description = '直前情報が非常に良好'
                elif pre_race_score <= 40:
                    factor_type = 'negative_concern'
                    description = '直前情報に懸念材料'
                else:
                    continue  # 普通の場合はスキップ
                
                notable_factors.append({
                    'horse_name': horse_name,
                    'factor_type': factor_type,
                    'description': description,
                    'pre_race_score': pre_race_score,
                    'key_factors': analysis.get('key_pre_race_factors', [])
                })
            
            return notable_factors
            
        except Exception as e:
            logger.error(f"Notable pre-race factors identification error: {str(e)}")
            return []

    # ヘルパーメソッド
    def _get_current_race_conditions(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """現在のレース条件取得"""
        return {
            'weather': race_data.get('weather', '晴'),
            'track_condition': race_data.get('track_condition', '良'),
            'temperature': race_data.get('temperature', 25),
            'humidity': race_data.get('humidity', 60),
            'wind_speed': race_data.get('wind_speed', 5)
        }

    def _evaluate_coat_condition(self, condition: str) -> float:
        """馬体の毛艶評価"""
        scores = {'excellent': 90, 'good': 75, 'average': 60, 'poor': 40}
        return scores.get(condition, 60)

    def _evaluate_walking_gait(self, gait: str) -> float:
        """歩様評価"""
        scores = {'smooth': 90, 'normal': 70, 'slightly_stiff': 50, 'concerning': 30}
        return scores.get(gait, 60)

    def _evaluate_alertness(self, alertness: str) -> float:
        """気合い・集中度評価"""
        scores = {'very_alert': 85, 'alert': 75, 'calm': 65, 'dull': 40}
        return scores.get(alertness, 60)

    def _evaluate_muscle_tone(self, tone: str) -> float:
        """筋肉の張り評価"""
        scores = {'excellent': 90, 'good': 75, 'average': 60, 'soft': 45}
        return scores.get(tone, 60)

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
            'pre_race_score': 0,
            'execution_time': 0
        }

    # ... その他のヘルパーメソッドは実装省略（実際の開発時に詳細実装）
