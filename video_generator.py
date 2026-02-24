from typing import Optional, Any
from pathlib import Path
from gradio_client import Client, handle_file


class VideoGenerator:
    def __init__(self):
        self.client = Client("https://wan-ai-wan2-2-animate.ms.show/")

    def generate_video(self,
                      image_path: str,
                      video_path: Optional[str] = None,
                      model_id: str = "wan2.2-animate-move",
                      model: str = "wan-pro",
                      timeout: int = 600) -> Any:
        """비디오와 이미지를 입력으로 받아 새로운 비디오 생성"""

        if not Path(image_path).exists():
            raise FileNotFoundError(f"이미지 파일이 없습니다: {image_path}")

        video_input = None
        if video_path and Path(video_path).exists():
            video_input = {"video": handle_file(video_path)}

        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"API 요청 중... (시도 {attempt + 1}/{max_retries})")

                # 클라이언트 재생성으로 연결 리셋
                if attempt > 0:
                    self.client = Client("https://wan-ai-wan2-2-animate.ms.show/")

                result = self.client.predict(
                    ref_img=handle_file(image_path),
                    video=video_input,
                    model_id=model_id,
                    model=model,
                    api_name="/predict"
                )
                return result

            except Exception as e:
                error_msg = str(e)
                print(f"시도 {attempt + 1} 실패: {error_msg}")

                if attempt == max_retries - 1:
                    return {"error": f"API 요청 실패 ({max_retries}번 시도): {error_msg}"}

                # 재시도 전 대기
                import time
                time.sleep(5)

    def save_generated_video(self, result: Any, output_path: str = "output.mp4") -> bool:
        """생성된 비디오를 파일로 저장"""
        try:
            if result and isinstance(result, (list, tuple)) and len(result) > 0:
                video_file = result[0]

                if hasattr(video_file, 'name'):
                    # 파일 객체인 경우
                    import shutil
                    shutil.copy2(video_file.name, output_path)
                    print(f"비디오가 저장되었습니다: {output_path}")
                    return True
                elif isinstance(video_file, str):
                    # 파일 경로인 경우
                    import shutil
                    shutil.copy2(video_file, output_path)
                    print(f"비디오가 저장되었습니다: {output_path}")
                    return True

        except Exception as e:
            print(f"비디오 저장 실패: {str(e)}")

        return False


def main():
    generator = VideoGenerator()

    # 예시 사용법
    image_path = "input_image.png"  # 입력 이미지 경로
    video_path = "input_video.mp4"  # 입력 비디오 경로 (선택사항)

    if not Path(image_path).exists():
        print(f"이미지 파일이 없습니다: {image_path}")
        return

    print("비디오 생성 중...")
    result = generator.generate_video(
        image_path=image_path,
        video_path=video_path if Path(video_path).exists() else None
    )

    if "error" in result:
        print(f"오류: {result['error']}")
    else:
        success = generator.save_generated_video(result, "generated_video.mp4")
        if success:
            print("비디오 생성이 완료되었습니다!")
        else:
            print("비디오 저장에 실패했습니다.")


if __name__ == "__main__":
    main()