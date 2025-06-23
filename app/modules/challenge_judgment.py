import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ChallengeAssessment:
    """格上挑戦評価データクラス"""
    horse_name: str
    current_class: str
    target_class: str
    challenge_type: str
    challenge_difficulty: float
    success_probability: float
    challenge_factors: List[str]
    risk_factors: List[str]
    challenge_score: float

class ChallengeJudgment:
    """格上挑戦判定システム v3.1【新機能・判定機能】"""
    
    def __init__(self):
        self.max_analysis_time = 15  # 秒
        
        # 格（クラス）階層定義
        self.class_hierarchy = {
            'maiden': 1,      # 未勝利
            '1勝': 2,         # 1勝クラス
            '2勝': 3,         # 2勝クラス
            '3勝': 4,         # 3勝クラス
            'OP': 5,          # オープン
            'G3': 6,          # G3
            'G2': 7,          # G2
            'G1': 8           # G1
        }
        
        # 挑戦タイプ別の成功要因
        self.challenge_success_factors = {
            'maiden_break': {
                'key_factors': ['血統', '調教内容', '騎手', '距離適性'],
                'base_success_rate': 0.33
            },
            'class_up': {
                'key_factors': ['前走内容', '着差', '騎手厩舎', '距離適性'],
                'base_success_rate': 0.25
            },
            'grade_challenge': {
                'key_factors': ['実績', '血統', '陣営', 'ローテーション'],
                'base_success_rate': 0.15
            },
            'big_challenge': {
                'key_factors': ['潜在能力', '血統', 'ステップレース', '陣営'],
                'base_success_rate': 0.08
            }
        }
        
        # 格上挑戦時の減額係数
        self.challenge_discount_factors = {
            1: 1.0,    # 同格
            2: 0.85,   # 1ランク上
            3: 0.65,   # 2ランク上
            4: 0.40,   # 3ランク上
            5: 0.20    # 4ランク以上
        }

    async def evaluate(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """格上挑戦判定実行（15秒）"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Starting challenge judgment analysis v3.1")
        
        try:
            horses = race_data.get('horses', [])
            if not horses:
                return self._create_error_result("No horses data")
            
            # 対象レースの格を判定
            target_race_class = self._determine_race_class(race_data)
            
            # 各馬の格上挑戦状況分析
            challenge_assessments = await self._assess_all_horses_challenge(horses, target_race_class, race_data)
            
            # 格上挑戦馬の分類
            challenge_classifications = self._classify_challenge_horses(challenge_assessments)
            
            # 成功可能性ランキング
            success_ranking = self._create_success_probability_ranking(challenge_assessments)
            
            # 注目格上挑戦馬抽出
            notable_challengers = self._identify_notable_challengers(challenge_assessments)
            
            # 格上挑戦リスク分析
            challenge_risks = self._analyze_challenge_risks(challenge_assessments)
            
            # レース全体の格上挑戦度評価
            race_challenge_level = self._evaluate_race_challenge_level(challenge_assessments, target_race_class)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Challenge judgment analysis completed in {execution_time:.2f}s")
            
            return {
                'status': 'completed',
                'execution_time': execution_time,
                'target_race_class': target_race_class,
                'challenge_assessments': challenge_assessments,
                'challenge_classifications': challenge_classifications,
                'success_ranking': success_ranking,
                'notable_challengers': notable_challengers,
                'challenge_risks': challenge_risks,
                'race_challenge_level': race_challenge_level,
                'challenge_summary': self._create_challenge_summary(
                    challenge_assessments, notable_challengers, challenge_risks
                )
            }
            
        except Exception as e:
            logger.error(f"Challenge judgment error: {str(e)}")
            return self._create_error_result(str(e))

    async def _assess_all_horses_challenge(self, horses: List[Dict], target_race_class: str, 
                                         race_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """全馬格上挑戦評価"""
        challenge_assessments = []
        
        for horse in horses:
            try:
                assessment = await self._assess_single_horse_challenge(horse, target_race_class, race_data)
                if assessment:
                    challenge_assessments.append(assessment)
            except Exception as e:
                logger.error(f"Single horse challenge assessment error: {str(e)}")
                continue
        
        return challenge_assessments

    async def _assess_single_horse_challenge(self, horse: Dict[str, Any], target_race_class: str, 
                                           race_data: Dict[str, Any]) -> Dict[str, Any]:
        """単一馬格上挑戦評価"""
        try:
            horse_name = horse.get('horse_name', '')
            
            # 馬の現在の格を判定
            current_class = await self._determine_horse_current_class(horse)
            
            # 挑戦レベル計算
            challenge_level = self._calculate_challenge_level(current_class, target_race_class)
            
            # 挑戦タイプ分類
            challenge_type = self._classify_challenge_type(current_class, target_race_class, challenge_level)
            
            # 挑戦難易度評価
            challenge_difficulty = self._evaluate_challenge_difficulty(challenge_level, challenge_type)
            
            # 成功可能性分析
            success_probability = await self._calculate_success_probability(
                horse, current_class, target_race_class, challenge_type, race_data
            )
            
            # 挑戦成功要因分析
            challenge_factors = await self._analyze_challenge_success_factors(
                horse, challenge_type, race_data
            )
            
            # リスク要因分析
            risk_factors = await self._analyze_challenge_risk_factors(
                horse, challenge_level, challenge_type
            )
            
            # 格上挑戦スコア計算
            challenge_score = self._calculate_challenge_score(
                success_probability, challenge_difficulty, challenge_factors, risk_factors
            )
            
            # 投資推奨調整
            investment_adjustment = self._calculate_investment_adjustment(challenge_level, success_probability)
            
            return {
                'horse_name': horse_name,
                'current_class': current_class,
                'target_class': target_race_class,
                'challenge_level': challenge_level,
                'challenge_type': challenge_type,
                'challenge_difficulty': challenge_difficulty,
                'success_probability': success_probability,
                'challenge_factors': challenge_factors,
                'risk_factors': risk_factors,
                'challenge_score': challenge_score,
                'challenge_rating': self._score_to_rating(challenge_score),
                'investment_adjustment': investment_adjustment,
                'challenge_recommendation': self._generate_challenge_recommendation(
                    challenge_type, success_probability, challenge_score
                )
            }
            
        except Exception as e:
            logger.error(f"Single horse challenge assessment error: {str(e)}")
            return None

    def _determine_race_class(self, race_data: Dict[str, Any]) -> str:
        """レースの格判定"""
        try:
            race_grade = race_data.get('grade', '')
            race_name = race_data.get('race_name', '')
            
            # G1/G2/G3の判定
            if 'G1' in race_grade or 'GI' in race_grade:
                return 'G1'
            elif 'G2' in race_grade or 'GII' in race_grade:
                return 'G2'
            elif 'G3' in race_grade or 'GIII' in race_grade:
                return 'G3'
            elif 'OP' in race_grade or 'オープン' in race_name:
                return 'OP'
            elif '3勝' in race_grade or '1600万' in race_name:
                return '3勝'
            elif '2勝' in race_grade or '1000万' in race_name:
                return '2勝'
            elif '1勝' in race_grade or '500万' in race_name:
                return '1勝'
            elif '未勝利' in race_grade or 'maiden' in race_grade.lower():
                return 'maiden'
            else:
                return 'OP'  # デフォルト
                
        except Exception as e:
            logger.error(f"Race class determination error: {str(e)}")
            return 'OP'

    async def _determine_horse_current_class(self, horse: Dict[str, Any]) -> str:
        """馬の現在の格判定"""
        try:
            # 実際の実装では過去成績から最高クラスを判定
            # ここでは模擬データを使用
            
            horse_name = horse.get('horse_name', '')
            
            # 模擬的な格判定（実際はデータベースから過去成績を取得）
            import random
            random.seed(hash(horse_name) % 1000)
            
            # 格の分布を現実的に設定
            class_distribution = {
                'maiden': 0.15,
                '1勝': 0.25,
                '2勝': 0.25,
                '3勝': 0.20,
                'OP': 0.10,
                'G3': 0.03,
                'G2': 0.015,
                'G1': 0.005
            }
            
            rand_value = random.random()
            cumulative = 0
            
            for class_name, probability in class_distribution.items():
                cumulative += probability
                if rand_value <= cumulative:
                    return class_name
            
            return '2勝'  # フォールバック
            
        except Exception as e:
            logger.error(f"Horse current class determination error: {str(e)}")
            return '2勝'

    def _calculate_challenge_level(self, current_class: str, target_class: str) -> int:
        """挑戦レベル計算"""
        try:
            current_level = self.class_hierarchy.get(current_class, 3)
            target_level = self.class_hierarchy.get(target_class, 5)
            
            challenge_level = target_level - current_level
            return max(0, challenge_level)
            
        except Exception as e:
            logger.error(f"Challenge level calculation error: {str(e)}")
            return 1

    def _classify_challenge_type(self, current_class: str, target_class: str, challenge_level: int) -> str:
        """挑戦タイプ分類"""
        try:
            if current_class == 'maiden':
                return 'maiden_break'
            elif challenge_level == 0:
                return 'same_class'
            elif challenge_level == 1:
                return 'class_up'
            elif challenge_level == 2 and target_class in ['G3', 'G2', 'G1']:
                return 'grade_challenge'
            elif challenge_level >= 3:
                return 'big_challenge'
            else:
                return 'class_up'
                
        except Exception as e:
            logger.error(f"Challenge type classification error: {str(e)}")
            return 'class_up'

    def _evaluate_challenge_difficulty(self, challenge_level: int, challenge_type: str) -> float:
        """挑戦難易度評価"""
        try:
            base_difficulty = {
                'same_class': 30,
                'maiden_break': 50,
                'class_up': 60,
                'grade_challenge': 80,
                'big_challenge': 95
            }.get(challenge_type, 60)
            
            # レベルによる追加難易度
            level_difficulty = min(20, challenge_level * 5)
            
            total_difficulty = min(100, base_difficulty + level_difficulty)
            return total_difficulty
            
        except Exception as e:
            logger.error(f"Challenge difficulty evaluation error: {str(e)}")
            return 60.0

    async def _calculate_success_probability(self, horse: Dict[str, Any], current_class: str, 
                                           target_class: str, challenge_type: str, 
                                           race_data: Dict[str, Any]) -> float:
        """成功可能性計算"""
        try:
            # ベース成功率
            base_success_rate = self.challenge_success_factors.get(challenge_type, {}).get('base_success_rate', 0.2)
            
            # 馬の能力評価（簡略化）
            ability_score = await self._evaluate_horse_ability_for_challenge(horse, race_data)
            
            # 能力による調整
            ability_adjustment = (ability_score - 50) / 100  # -0.5 to +0.5の範囲
            
            # 血統による調整
            bloodline_adjustment = await self._evaluate_bloodline_for_challenge(horse, target_class)
            
            # 陣営による調整
            trainer_jockey_adjustment = await self._evaluate_trainer_jockey_for_challenge(horse)
            
            # 総合成功確率
            success_probability = base_success_rate + ability_adjustment + bloodline_adjustment + trainer_jockey_adjustment
            
            return max(0.01, min(0.8, success_probability))
            
        except Exception as e:
            logger.error(f"Success probability calculation error: {str(e)}")
            return 0.2

    async def _analyze_challenge_success_factors(self, horse: Dict[str, Any], challenge_type: str, 
                                               race_data: Dict[str, Any]) -> List[str]:
        """挑戦成功要因分析"""
        try:
            success_factors = []
            
            # 挑戦タイプ別の要因チェック
            if challenge_type == 'maiden_break':
                if await self._check_bloodline_potential(horse):
                    success_factors.append('血統的ポテンシャル')
                if await self._check_training_improvement(horse):
                    success_factors.append('調教内容の向上')
                if await self._check_distance_suitability(horse, race_data):
                    success_factors.append('距離適性良好')
            
            elif challenge_type in ['class_up', 'grade_challenge']:
                if await self._check_recent_form(horse):
                    success_factors.append('近走好内容')
                if await self._check_jockey_trainer_strength(horse):
                    success_factors.append('強力な陣営')
                if await self._check_class_experience(horse):
                    success_factors.append('上級戦経験')
            
            elif challenge_type == 'big_challenge':
                if await self._check_exceptional_ability(horse):
                    success_factors.append('突出した能力')
                if await self._check_elite_connections(horse):
                    success_factors.append('エリート陣営')
                if await self._check_perfect_conditions(horse, race_data):
                    success_factors.append('理想的条件')
            
            return success_factors[:5]  # 最大5つ
            
        except Exception as e:
            logger.error(f"Challenge success factors analysis error: {str(e)}")
            return []

    def _calculate_challenge_score(self, success_probability: float, challenge_difficulty: float, 
                                 challenge_factors: List[str], risk_factors: List[str]) -> float:
        """格上挑戦スコア計算"""
        try:
            # ベーススコア（成功可能性ベース）
            base_score = success_probability * 100
            
            # 難易度による調整
            difficulty_adjustment = (100 - challenge_difficulty) * 0.3
            
            # 成功要因によるボーナス
            factor_bonus = len(challenge_factors) * 5
            
            # リスク要因によるペナルティ
            risk_penalty = len(risk_factors) * 8
            
            # 総合スコア
            challenge_score = base_score + difficulty_adjustment + factor_bonus - risk_penalty
            
            return max(0, min(100, challenge_score))
            
        except Exception as e:
            logger.error(f"Challenge score calculation error: {str(e)}")
            return 30.0

    def _identify_notable_challengers(self, challenge_assessments: List[Dict]) -> List[Dict]:
        """注目格上挑戦馬特定"""
        try:
            notable_challengers = []
            
            for assessment in challenge_assessments:
                challenge_level = assessment.get('challenge_level', 0)
                success_probability = assessment.get('success_probability', 0)
                challenge_score = assessment.get('challenge_score', 0)
                
                # 注目基準
                if (challenge_level >= 1 and  # 格上挑戦
                    success_probability >= 0.2 and  # 成功可能性20%以上
                    challenge_score >= 50):  # チャレンジスコア50以上
                    
                    notable_challengers.append({
                        'horse_name': assessment.get('horse_name', ''),
                        'challenge_type': assessment.get('challenge_type', ''),
                        'success_probability': success_probability,
                        'challenge_score': challenge_score,
                        'highlight_reason': self._generate_highlight_reason(assessment)
                    })
            
            # スコア順でソート
            notable_challengers.sort(key=lambda x: x['challenge_score'], reverse=True)
            
            return notable_challengers[:3]  # 上位3頭
            
        except Exception as e:
            logger.error(f"Notable challengers identification error: {str(e)}")
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
            'target_race_class': 'unknown',
            'challenge_assessments': [],
            'execution_time': 0
        }

    # ... その他のヘルパーメソッドは実装省略（実際の開発時に詳細実装）
    async def _evaluate_horse_ability_for_challenge(self, horse: Dict, race_data: Dict) -> float:
        """挑戦用能力評価"""
        return 60.0  # 簡略化

    async def _evaluate_bloodline_for_challenge(self, horse: Dict, target_class: str) -> float:
        """挑戦用血統評価"""
        return 0.05  # 簡略化

    async def _evaluate_trainer_jockey_for_challenge(self, horse: Dict) -> float:
        """挑戦用陣営評価"""
        return 0.02  # 簡略化

    # ... その他も同様に簡略化実装
    async def _check_bloodline_potential(self, horse: Dict) -> bool:
        return True

    async def _check_training_improvement(self, horse: Dict) -> bool:
        return True

    async def _check_distance_suitability(self, horse: Dict, race_data: Dict) -> bool:
        return True

    def _generate_highlight_reason(self, assessment: Dict) -> str:
        return "格上挑戦で期待値高"

    # ... その他のチェック系メソッドも簡略化実装
