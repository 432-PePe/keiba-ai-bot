import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class DataValidation:
    """データ検証システム v3.1【品質保証・Critical対応】"""
    
    def __init__(self):
        self.quality_thresholds = {
            'required_completeness': 1.0,     # 100%必須
            'recommended_completeness': 0.95,  # 95%推奨
            'encoding_quality': 0.98,         # 98%文字化け対策
            'overall_minimum': 0.94           # 94%総合最低基準
        }
        
        # 必須フィールド定義
        self.required_race_fields = [
            'race_name', 'track', 'distance', 'surface', 
            'horses', 'start_time', 'weather'
        ]
        
        self.required_horse_fields = [
            'horse_name', 'horse_number', 'jockey', 'trainer',
            'age', 'weight', 'barrier'
        ]

    def validate_race_data(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """レースデータ品質検証"""
        try:
            logger.info("Starting race data validation")
            
            if not race_data:
                return self._create_validation_error("No race data provided")
            
            # 基本構造検証
            structure_result = self._validate_data_structure(race_data)
            
            # 文字化け検証
            encoding_result = self._validate_encoding_quality(race_data)
            
            # 完全性検証
            completeness_result = self._validate_data_completeness(race_data)
            
            # 論理整合性検証
            consistency_result = self._validate_data_consistency(race_data)
            
            # 総合評価
            overall_quality = self._calculate_overall_quality(
                structure_result, encoding_result, completeness_result, consistency_result
            )
            
            is_valid = overall_quality >= self.quality_thresholds['overall_minimum']
            
            return {
                'is_valid': is_valid,
                'overall_quality': overall_quality,
                'structure_validation': structure_result,
                'encoding_validation': encoding_result,
                'completeness_validation': completeness_result,
                'consistency_validation': consistency_result,
                'errors': self._collect_all_errors(
                    structure_result, encoding_result, completeness_result, consistency_result
                ),
                'warnings': self._collect_all_warnings(
                    structure_result, encoding_result, completeness_result, consistency_result
                ),
                'validation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Race data validation error: {str(e)}")
            return self._create_validation_error(str(e))

    def _validate_data_structure(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """データ構造検証"""
        errors = []
        warnings = []
        
        try:
            # レース基本情報チェック
            for field in self.required_race_fields:
                if field not in race_data:
                    errors.append(f"Required field missing: {field}")
                elif not race_data[field]:
                    errors.append(f"Required field empty: {field}")
            
            # 馬データ構造チェック
            horses = race_data.get('horses', [])
            if not isinstance(horses, list):
                errors.append("Horses data must be a list")
            elif len(horses) == 0:
                errors.append("No horses data found")
            else:
                for i, horse in enumerate(horses):
                    if not isinstance(horse, dict):
                        errors.append(f"Horse {i+1}: Invalid data structure")
                        continue
                    
                    for field in self.required_horse_fields:
                        if field not in horse:
                            errors.append(f"Horse {i+1}: Missing field {field}")
                        elif not horse[field]:
                            warnings.append(f"Horse {i+1}: Empty field {field}")
            
            structure_score = max(0, 1.0 - (len(errors) * 0.1 + len(warnings) * 0.05))
            
            return {
                'score': structure_score,
                'errors': errors,
                'warnings': warnings,
                'status': 'passed' if len(errors) == 0 else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Structure validation error: {str(e)}")
            return {
                'score': 0.0,
                'errors': [f"Structure validation failed: {str(e)}"],
                'warnings': [],
                'status': 'error'
            }

    def _validate_encoding_quality(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """文字エンコーディング品質検証"""
        errors = []
        warnings = []
        
        try:
            # レース名の文字化けチェック
            race_name = race_data.get('race_name', '')
            if not self._is_valid_japanese_text(race_name):
                errors.append(f"Race name encoding invalid: {race_name}")
            
            # 馬名の文字化けチェック
            horses = race_data.get('horses', [])
            invalid_count = 0
            
            for horse in horses:
                horse_name = horse.get('horse_name', '')
                jockey_name = horse.get('jockey', '')
                trainer_name = horse.get('trainer', '')
                
                if not self._is_valid_japanese_text(horse_name):
                    invalid_count += 1
                    warnings.append(f"Invalid horse name: {horse_name}")
                
                if not self._is_valid_japanese_text(jockey_name):
                    invalid_count += 1
                    warnings.append(f"Invalid jockey name: {jockey_name}")
                
                if not self._is_valid_japanese_text(trainer_name):
                    invalid_count += 1
                    warnings.append(f"Invalid trainer name: {trainer_name}")
            
            total_text_fields = len(horses) * 3 + 1  # 馬名+騎手名+調教師名+レース名
            encoding_score = max(0, 1.0 - (invalid_count / total_text_fields))
            
            return {
                'score': encoding_score,
                'errors': errors,
                'warnings': warnings,
                'invalid_count': invalid_count,
                'total_fields': total_text_fields,
                'status': 'passed' if encoding_score >= self.quality_thresholds['encoding_quality'] else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Encoding validation error: {str(e)}")
            return {
                'score': 0.0,
                'errors': [f"Encoding validation failed: {str(e)}"],
                'warnings': [],
                'status': 'error'
            }

    def _validate_data_completeness(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """データ完全性検証"""
        try:
            required_complete = 0
            required_total = len(self.required_race_fields)
            
            # レース基本情報の完全性
            for field in self.required_race_fields:
                if field in race_data and race_data[field]:
                    required_complete += 1
            
            # 馬データの完全性
            horses = race_data.get('horses', [])
            horse_completeness = 0
            
            if horses:
                for horse in horses:
                    horse_complete = 0
                    for field in self.required_horse_fields:
                        if field in horse and horse[field]:
                            horse_complete += 1
                    horse_completeness += horse_complete / len(self.required_horse_fields)
                horse_completeness /= len(horses)
            
            # 総合完全性スコア
            race_completeness = required_complete / required_total
            overall_completeness = (race_completeness * 0.3 + horse_completeness * 0.7)
            
            return {
                'score': overall_completeness,
                'race_completeness': race_completeness,
                'horse_completeness': horse_completeness,
                'required_fields_complete': f"{required_complete}/{required_total}",
                'status': 'passed' if overall_completeness >= self.quality_thresholds['required_completeness'] else 'failed',
                'errors': [] if overall_completeness >= self.quality_thresholds['required_completeness'] else 
                         [f"Data completeness insufficient: {overall_completeness:.2%}"],
                'warnings': []
            }
            
        except Exception as e:
            logger.error(f"Completeness validation error: {str(e)}")
            return {
                'score': 0.0,
                'errors': [f"Completeness validation failed: {str(e)}"],
                'warnings': [],
                'status': 'error'
            }

    def _validate_data_consistency(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """データ論理整合性検証"""
        errors = []
        warnings = []
        
        try:
            horses = race_data.get('horses', [])
            
            # 馬番重複チェック
            horse_numbers = []
            for horse in horses:
                num = horse.get('horse_number')
                if num in horse_numbers:
                    errors.append(f"Duplicate horse number: {num}")
                horse_numbers.append(num)
            
            # 枠番範囲チェック
            for horse in horses:
                barrier = horse.get('barrier')
                if barrier and (not isinstance(barrier, (int, str)) or 
                              (isinstance(barrier, str) and not barrier.isdigit()) or
                              int(str(barrier)) < 1 or int(str(barrier)) > 8):
                    warnings.append(f"Invalid barrier number: {barrier}")
            
            # 年齢範囲チェック
            for horse in horses:
                age = horse.get('age')
                if age and (not isinstance(age, (int, str)) or
                           (isinstance(age, str) and not age.isdigit()) or
                           int(str(age)) < 2 or int(str(age)) > 10):
                    warnings.append(f"Unusual horse age: {age}")
            
            consistency_score = max(0, 1.0 - (len(errors) * 0.2 + len(warnings) * 0.1))
            
            return {
                'score': consistency_score,
                'errors': errors,
                'warnings': warnings,
                'status': 'passed' if len(errors) == 0 else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Consistency validation error: {str(e)}")
            return {
                'score': 0.0,
                'errors': [f"Consistency validation failed: {str(e)}"],
                'warnings': [],
                'status': 'error'
            }

    def validate_analysis_results(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析結果の検証"""
        try:
            logger.info("Starting analysis results validation")
            
            errors = []
            warnings = []
            
            # 基本構造チェック
            if not isinstance(analysis_results, dict):
                errors.append("Analysis results must be a dictionary")
                return self._create_validation_error("Invalid analysis results structure")
            
            # 必須フィールドチェック
            required_fields = ['status', 'recommendations']
            for field in required_fields:
                if field not in analysis_results:
                    errors.append(f"Missing required field: {field}")
            
            # 推奨結果の妥当性チェック
            recommendations = analysis_results.get('recommendations', [])
            if not isinstance(recommendations, list):
                errors.append("Recommendations must be a list")
            elif len(recommendations) == 0:
                warnings.append("No recommendations generated")
            
            # スコア範囲チェック
            for key, value in analysis_results.items():
                if 'score' in key.lower() and isinstance(value, (int, float)):
                    if not (0 <= value <= 100):
                        warnings.append(f"Score out of range: {key}={value}")
            
            validation_score = max(0, 1.0 - (len(errors) * 0.3 + len(warnings) * 0.1))
            
            return {
                'is_valid': len(errors) == 0,
                'validation_score': validation_score,
                'errors': errors,
                'warnings': warnings,
                'recommendations_count': len(recommendations) if isinstance(recommendations, list) else 0,
                'validation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analysis results validation error: {str(e)}")
            return self._create_validation_error(str(e))

    # ヘルパーメソッド
    def _is_valid_japanese_text(self, text: str) -> bool:
        """日本語テキストの妥当性チェック"""
        if not text or not isinstance(text, str):
            return True  # 空文字は許可
        
        # 日本語文字、英数字、記号の範囲チェック
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u0020-\u007F]+')
        return bool(japanese_pattern.fullmatch(text))

    def _calculate_overall_quality(self, *validation_results) -> float:
        """総合品質スコア計算"""
        try:
            total_score = 0
            valid_results = 0
            
            for result in validation_results:
                if isinstance(result, dict) and 'score' in result:
                    total_score += result['score']
                    valid_results += 1
            
            return total_score / valid_results if valid_results > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Overall quality calculation error: {str(e)}")
            return 0.0

    def _collect_all_errors(self, *validation_results) -> List[str]:
        """全エラーの収集"""
        all_errors = []
        for result in validation_results:
            if isinstance(result, dict) and 'errors' in result:
                all_errors.extend(result['errors'])
        return all_errors

    def _collect_all_warnings(self, *validation_results) -> List[str]:
        """全警告の収集"""
        all_warnings = []
        for result in validation_results:
            if isinstance(result, dict) and 'warnings' in result:
                all_warnings.extend(result['warnings'])
        return all_warnings

    def _create_validation_error(self, error_msg: str) -> Dict[str, Any]:
        """検証エラー結果作成"""
        return {
            'is_valid': False,
            'overall_quality': 0.0,
            'errors': [error_msg],
            'warnings': [],
            'validation_timestamp': datetime.now().isoformat()
        }
