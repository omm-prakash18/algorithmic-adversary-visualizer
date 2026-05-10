from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import subprocess
import os
import tempfile
import time

class CodeExecutionView(APIView):
    def post(self, request):
        user_code = request.data.get('user_code', '')
        if not user_code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)

        # In a real production environment, this MUST run in a Docker container.
        # Fallback for current environment: local subprocess with timeout.
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'solution.cpp')
            exec_path = os.path.join(temp_dir, 'solution.exe')
            
            with open(file_path, 'w') as f:
                f.write(user_code)

            # Check if g++ is available
            try:
                subprocess.run(['g++', '--version'], capture_output=True, timeout=1)
            except FileNotFoundError:
                return Response({
                    'status': 'mock_success',
                    'stdout': 'Starting BST Visualization...\n(Mocked output: g++ not found on host)',
                    'stderr': '',
                    'execution_time_ms': 0.0,
                    'memory_used_kb': 0
                }, status=status.HTTP_200_OK)

            start_time = time.time()
            try:
                # Compile
                compile_proc = subprocess.run(
                    ['g++', file_path, '-o', exec_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if compile_proc.returncode != 0:
                    return Response({
                        'status': 'compilation_error',
                        'stdout': compile_proc.stdout,
                        'stderr': compile_proc.stderr,
                    }, status=status.HTTP_200_OK)
                
                # Execute
                try:
                    exec_proc = subprocess.run(
                        [exec_path],
                        capture_output=True,
                        text=True,
                        timeout=2,
                        errors='replace'
                    )
                    
                    execution_time = (time.time() - start_time) * 1000
                    
                    return Response({
                        'status': 'success',
                        'stdout': exec_proc.stdout,
                        'stderr': exec_proc.stderr,
                        'execution_time_ms': round(execution_time, 2),
                        'memory_used_kb': 1024 # Placeholder
                    }, status=status.HTTP_200_OK)
                except Exception as exec_err:
                     return Response({
                        'status': 'execution_error',
                        'error': f'Failed to execute binary: {str(exec_err)}'
                    }, status=status.HTTP_200_OK)
                
            except subprocess.TimeoutExpired:
                return Response({
                    'status': 'timeout',
                    'error': 'Execution exceeded time limit'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
