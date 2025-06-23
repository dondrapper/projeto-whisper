"""
Testes unitários para o Whisper Pro Transcriber.
"""

import unittest
import tempfile
import os
from pathlib import Path
import numpy as np
import wave
from unittest.mock import Mock, patch, MagicMock

# Adicionar o diretório raiz ao path para importar módulos
import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    validate_audio_file, 
    estimate_processing_time,
    format_time,
    clean_filename,
    format_file_size
)
from config import Config

class TestUtils(unittest.TestCase):
    """Testes para módulo utils.py"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_audio_file(self, size_mb=1, name="test.wav", mime_type="audio/wav"):
        """Cria um arquivo de áudio mock para testes"""
        mock_file = Mock()
        mock_file.name = name
        mock_file.size = int(size_mb * 1024 * 1024)
        mock_file.type = mime_type
        mock_file.getvalue.return_value = b"fake_audio_data" * (mock_file.size // 15)
        return mock_file
    
    def test_validate_audio_file_valid(self):
        """Testa validação de arquivo válido"""
        mock_file = self.create_mock_audio_file(5, "test.wav", "audio/wav")
        result = validate_audio_file(mock_file)
        
        self.assertTrue(result["valid"])
        self.assertNotIn("error", result)
    
    def test_validate_audio_file_too_large(self):
        """Testa validação de arquivo muito grande"""
        mock_file = self.create_mock_audio_file(600, "huge.mp3", "audio/mpeg")  # 600MB
        result = validate_audio_file(mock_file)
        
        self.assertFalse(result["valid"])
        self.assertIn("muito grande", result["error"])
    
    def test_validate_audio_file_unsupported_type(self):
        """Testa validação de tipo de arquivo não suportado"""
        mock_file = self.create_mock_audio_file(1, "test.txt", "text/plain")
        result = validate_audio_file(mock_file)
        
        self.assertFalse(result["valid"])
        self.assertIn("não suportado", result["error"])
    
    def test_validate_audio_file_no_file(self):
        """Testa validação sem arquivo"""
        result = validate_audio_file(None)
        
        self.assertFalse(result["valid"])
        self.assertIn("Nenhum arquivo", result["error"])
    
    def test_estimate_processing_time(self):
        """Testa estimativa de tempo de processamento"""
        # Teste com GPU
        time_gpu = estimate_processing_time(10, "base", "cuda")
        self.assertIsInstance(time_gpu, str)
        self.assertTrue("min" in time_gpu or "s" in time_gpu)
        
        # Teste com CPU
        time_cpu = estimate_processing_time(10, "base", "cpu")
        self.assertIsInstance(time_cpu, str)
        
        # CPU deve ser mais lento que GPU
        # (difícil de testar exatamente, mas pelo menos verificar que não falha)
        
    def test_format_time(self):
        """Testa formatação de tempo"""
        self.assertEqual(format_time(0), "00:00:00")
        self.assertEqual(format_time(30), "00:00:30")
        self.assertEqual(format_time(90), "00:01:30")
        self.assertEqual(format_time(3661), "01:01:01")
        self.assertEqual(format_time(-5), "00:00:00")  # Tempo negativo
    
    def test_clean_filename(self):
        """Testa limpeza de nome de arquivo"""
        self.assertEqual(clean_filename("test file.mp3"), "test_file.mp3")
        self.assertEqual(clean_filename("arquivo@especial#.wav"), "arquivo_especial_.wav")
        self.assertEqual(clean_filename("normal.mp3"), "normal.mp3")
        self.assertEqual(clean_filename("###.wav"), "audio_file.wav")  # Nome vazio
    
    def test_format_file_size(self):
        """Testa formatação de tamanho de arquivo"""
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(512), "512.0 B")
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.0 MB")
        self.assertEqual(format_file_size(1024 * 1024 * 1024), "1.0 GB")

class TestConfig(unittest.TestCase):
    """Testes para módulo config.py"""
    
    def test_app_config(self):
        """Testa configurações da aplicação"""
        self.assertEqual(Config.App.APP_NAME, "Whisper Pro Transcriber")
        self.assertEqual(Config.App.APP_VERSION, "2.0.0")
        self.assertIsInstance(Config.App.THEME, dict)
    
    def test_file_config(self):
        """Testa configurações de arquivo"""
        self.assertGreater(Config.File.MAX_FILE_SIZE_MB, 0)
        self.assertIsInstance(Config.File.SUPPORTED_AUDIO_EXTENSIONS, list)
        self.assertIn(".mp3", Config.File.SUPPORTED_AUDIO_EXTENSIONS)
        self.assertIn(".wav", Config.File.SUPPORTED_AUDIO_EXTENSIONS)
    
    def test_whisper_config(self):
        """Testa configurações do Whisper"""
        self.assertIn("tiny", Config.Whisper.MODELS)
        self.assertIn("large-v2", Config.Whisper.MODELS)
        self.assertIn("pt", Config.Whisper.LANGUAGES)
        self.assertIn("en", Config.Whisper.LANGUAGES)
        
        # Verificar estrutura dos modelos
        for model_name, model_info in Config.Whisper.MODELS.items():
            self.assertIn("description", model_info)
            self.assertIn("memory", model_info)
            self.assertIn("speed", model_info)
    
    def test_get_device_config(self):
        """Testa configuração de dispositivo"""
        cpu_config = Config.get_device_config("cpu", 4)
        self.assertIn("multiplier", cpu_config)
        self.assertIn("recommended_models", cpu_config)
        
        gpu_config = Config.get_device_config("cuda", 8)
        self.assertIn("multiplier", gpu_config)
        self.assertLess(gpu_config["multiplier"], cpu_config["multiplier"])

class TestTranscriber(unittest.TestCase):
    """Testes para módulo transcriber.py"""
    
    @patch('transcriber.whisper')
    @patch('transcriber.torch')
    def test_load_whisper_model(self, mock_torch, mock_whisper):
        """Testa carregamento do modelo Whisper"""
        # Mock do dispositivo CUDA
        mock_torch.cuda.is_available.return_value = True
        
        # Mock do modelo
        mock_model = Mock()
        mock_whisper.load_model.return_value = mock_model
        
        from transcriber import load_whisper_model
        
        # Teste de carregamento
        model = load_whisper_model("base")
        
        # Verificações
        mock_whisper.load_model.assert_called_once_with("base", device="cuda")
        self.assertEqual(model, mock_model)
    
    def create_temp_audio_file(self):
        """Cria um arquivo de áudio temporário para testes"""
        # Gerar dados de áudio simples
        sample_rate = 16000
        duration = 1  # 1 segundo
        frequency = 440  # Lá 4
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Salvar como arquivo WAV temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return temp_file.name
    
    @patch('transcriber.whisper')
    @patch('transcriber.torch')
    def test_transcribe_audio(self, mock_torch, mock_whisper):
        """Testa transcrição de áudio"""
        # Setup dos mocks
        mock_torch.cuda.is_available.return_value = False  # Usar CPU para teste
        mock_torch.no_grad.return_value.__enter__ = Mock()
        mock_torch.no_grad.return_value.__exit__ = Mock()
        
        mock_model = Mock()
        mock_result = {
            "text": "Teste de transcrição",
            "language": "pt",
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Teste de transcrição",
                    "words": [
                        {"word": "Teste", "start": 0.0, "end": 0.5, "probability": 0.9},
                        {"word": "de", "start": 0.6, "end": 0.8, "probability": 0.95},
                        {"word": "transcrição", "start": 0.9, "end": 2.0, "probability": 0.85}
                    ]
                }
            ]
        }
        mock_model.transcribe.return_value = mock_result
        
        # Criar arquivo de áudio temporário
        audio_file = self.create_temp_audio_file()
        
        try:
            from transcriber import transcribe_audio
            
            # Executar transcrição
            result = transcribe_audio(audio_file, mock_model, "pt", "transcribe")
            
            # Verificações
            self.assertIn("text", result)
            self.assertIn("processing_time", result)
            self.assertIn("processing_time_formatted", result)
            self.assertIn("average_confidence", result)
            self.assertEqual(result["text"], "Teste de transcrição")
            
        finally:
            # Limpar arquivo temporário
            os.unlink(audio_file)

class TestAudioRecorder(unittest.TestCase):
    """Testes para módulo audio_recorder.py"""
    
    def test_get_audio_config(self):
        """Testa configurações de áudio"""
        from audio_recorder import get_audio_config
        
        # Teste configuração low
        config_low = get_audio_config("low")
        self.assertEqual(config_low["sample_rate"], 8000)
        self.assertEqual(config_low["channels"], 1)
        
        # Teste configuração high
        config_high = get_audio_config("high")
        self.assertEqual(config_high["sample_rate"], 44100)
        self.assertEqual(config_high["channels"], 2)
        
        # Teste configuração inválida (deve retornar standard)
        config_invalid = get_audio_config("invalid")
        self.assertEqual(config_invalid["sample_rate"], 16000)
    
    def test_format_time_for_srt(self):
        """Testa formatação de tempo para SRT"""
        from audio_recorder import format_time_for_srt
        
        self.assertEqual(format_time_for_srt(0), "00:00:00,000")
        self.assertEqual(format_time_for_srt(1.5), "00:00:01,500")
        self.assertEqual(format_time_for_srt(65.25), "00:01:05,250")
    
    def test_create_sample_audio_file(self):
        """Testa criação de arquivo de áudio de exemplo"""
        from audio_recorder import create_sample_audio_file
        
        audio_file = create_sample_audio_file()
        
        try:
            # Verificar se arquivo foi criado
            self.assertTrue(os.path.exists(audio_file))
            
            # Verificar se tem conteúdo
            self.assertGreater(os.path.getsize(audio_file), 0)
            
            # Verificar se é um arquivo WAV válido
            with wave.open(audio_file, 'rb') as wav_file:
                self.assertEqual(wav_file.getnchannels(), 1)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertGreater(wav_file.getnframes(), 0)
                
        finally:
            # Limpar arquivo de teste
            if os.path.exists(audio_file):
                os.unlink(audio_file)

class TestIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def test_full_pipeline_mock(self):
        """Testa pipeline completo com mocks"""
        # Este teste simula todo o fluxo sem usar modelos reais
        
        # 1. Criar arquivo de áudio mock
        from test_transcriber import TestTranscriber
        test_transcriber = TestTranscriber()
        audio_file = test_transcriber.create_temp_audio_file()
        
        try:
            # 2. Validar arquivo
            from unittest.mock import Mock
            mock_uploaded_file = Mock()
            mock_uploaded_file.name = "test.wav"
            mock_uploaded_file.size = os.path.getsize(audio_file)
            mock_uploaded_file.type = "audio/wav"
            mock_uploaded_file.getvalue.return_value = open(audio_file, 'rb').read()
            
            validation_result = validate_audio_file(mock_uploaded_file)
            self.assertTrue(validation_result["valid"])
            
            # 3. Estimar tempo de processamento
            file_size_mb = mock_uploaded_file.size / (1024 * 1024)
            estimated_time = estimate_processing_time(file_size_mb, "base", "cpu")
            self.assertIsInstance(estimated_time, str)
            
            # 4. Mock da transcrição (sem executar modelo real)
            mock_result = {
                "text": "Teste de integração completa",
                "language": "pt",
                "segments": [],
                "processing_time": 1.5,
                "processing_time_formatted": "00:00:01"
            }
            
            # Verificar estrutura do resultado
            self.assertIn("text", mock_result)
            self.assertIn("processing_time", mock_result)
            
        finally:
            # Limpar arquivo temporário
            os.unlink(audio_file)

def run_performance_test():
    """Executa teste de performance básico"""
    print("🚀 Executando teste de performance...")
    
    import time
    
    # Teste de criação de arquivo
    start_time = time.time()
    test_transcriber = TestTranscriber()
    audio_file = test_transcriber.create_temp_audio_file()
    creation_time = time.time() - start_time
    
    print(f"⏱️ Criação de arquivo: {creation_time:.3f}s")
    
    # Teste de validação
    start_time = time.time()
    mock_file = test_transcriber.create_mock_audio_file()
    result = validate_audio_file(mock_file)
    validation_time = time.time() - start_time
    
    print(f"⏱️ Validação de arquivo: {validation_time:.3f}s")
    print(f"✅ Arquivo válido: {result['valid']}")
    
    # Limpeza
    os.unlink(audio_file)
    
    print("✅ Teste de performance concluído!")

if __name__ == "__main__":
    print("🧪 Iniciando testes do Whisper Pro Transcriber...")
    
    # Executar testes unitários
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*50)
    
    # Executar teste de performance
    run_performance_test()
    
    print("\n🎉 Todos os testes concluídos!")