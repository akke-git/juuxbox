"""
Error Handler
=============
전역 에러 핸들링 및 사용자 알림
"""

import logging
import sys
import traceback
from typing import Callable, Optional

from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class ErrorHandler(QObject):
    """
    전역 에러 핸들러
    
    예외를 캐치하고 사용자에게 적절한 메시지를 표시합니다.
    """
    
    error_occurred = Signal(str, str)  # (title, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._install_exception_hook()
        self.error_occurred.connect(self._show_error_dialog)
        
    def _install_exception_hook(self):
        """전역 예외 훅 설치"""
        self._original_hook = sys.excepthook
        sys.excepthook = self._exception_hook
        
    def _exception_hook(self, exc_type, exc_value, exc_tb):
        """예외 발생 시 호출"""
        # 로깅
        logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_tb)
        )
        
        # 사용자에게 표시
        error_msg = str(exc_value)
        self.error_occurred.emit("오류 발생", error_msg)
        
        # 원본 훅도 호출 (디버깅용)
        self._original_hook(exc_type, exc_value, exc_tb)
        
    def _show_error_dialog(self, title: str, message: str):
        """에러 다이얼로그 표시"""
        app = QApplication.instance()
        if app:
            QMessageBox.critical(None, title, message)
            
    def handle_audio_error(self, error: str):
        """오디오 관련 에러 처리"""
        logger.error(f"오디오 에러: {error}")
        self.error_occurred.emit(
            "오디오 에러",
            f"오디오 재생 중 문제가 발생했습니다:\n{error}"
        )
        
    def handle_device_error(self, device_name: str):
        """장치 연결 에러 처리"""
        logger.error(f"장치 에러: {device_name}")
        self.error_occurred.emit(
            "장치 연결 실패",
            f"오디오 장치 '{device_name}'에 연결할 수 없습니다.\n"
            "다른 앱이 장치를 사용 중이거나 연결이 해제되었을 수 있습니다."
        )
        
    def handle_file_error(self, file_path: str, error: str):
        """파일 관련 에러 처리"""
        logger.warning(f"파일 에러: {file_path} - {error}")
        # 파일 에러는 조용히 스킵 (다음 곡 재생)
        
    def cleanup(self):
        """정리"""
        sys.excepthook = self._original_hook


# 전역 인스턴스
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """전역 에러 핸들러 가져오기"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler
