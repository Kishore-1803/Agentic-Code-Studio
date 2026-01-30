import subprocess
import os
import tempfile
import sys
import time
import re

class TesterAgent:
    def __init__(self):
        pass

    def run_test(self, code: str, test_code: str = "", language: str = "python") -> dict:
        """
        Executes the provided code. Supports Python, C++, and Java.
        """
        if language.lower() in ['c++', 'cpp']:
            return self._run_cpp(code, test_code)
        elif language.lower() == 'java':
            return self._run_java(code, test_code)
        
        # Default to Python logic
        return self._run_python(code, test_code)

    def _run_python(self, code: str, test_code: str):
        # Create a temporary file to run
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            if test_code:
                f.write("\n\n" + test_code)
            temp_path = f.name

        # start_time = time.time()
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Execution timed out."
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _run_cpp(self, code: str, test_code: str):
        # Create source file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False, encoding='utf-8') as f:
            f.write(code)
            if test_code:
                f.write("\n\n" + test_code)
            src_path = f.name
            exe_path = src_path + ".exe"

        try:
            # Compile
            compile_res = subprocess.run(
                ["g++", src_path, "-o", exe_path],
                capture_output=True,
                text=True
            )
            
            if compile_res.returncode != 0:
                 return {
                    "success": False, 
                    "output": "", 
                    "error": f"Compilation Error:\n{compile_res.stderr}"
                 }
                 
            run_res = subprocess.run(
                [exe_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": run_res.returncode == 0,
                "output": run_res.stdout,
                "error": run_res.stderr
            }
            
        except FileNotFoundError:
             return {
                "success": False, 
                "output": "", 
                "error": "g++ compiler not found. Please install MinGW or similar."
             }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
        finally:
            if os.path.exists(src_path):
                os.remove(src_path)
            if os.path.exists(exe_path):
                os.remove(exe_path)

    def _run_java(self, code: str, test_code: str):
        # Extract class name to name the file
        class_name = "Main"
        match = re.search(r'public\s+class\s+(\w+)', code)
        if match:
            class_name = match.group(1)
        else:
            match = re.search(r'class\s+(\w+)', code)
            if match:
                class_name = match.group(1)

        # Create temporary directory to hold the file
        with tempfile.TemporaryDirectory() as temp_dir:
            src_file_name = f"{class_name}.java"
            src_path = os.path.join(temp_dir, src_file_name)
            
            with open(src_path, 'w', encoding='utf-8') as f:
                f.write(code)
                if test_code:
                    f.write("\n\n" + test_code)
            
            try:
                # Compile
                compile_res = subprocess.run(
                    ["javac", src_path],
                    capture_output=True,
                    text=True
                )
                
                if compile_res.returncode != 0:
                     return {
                        "success": False, 
                        "output": "", 
                        "error": f"Compilation Error:\n{compile_res.stderr}"
                     }
                
                run_res = subprocess.run(
                    ["java", "-cp", temp_dir, class_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                return {
                    "success": run_res.returncode == 0,
                    "output": run_res.stdout,
                    "error": run_res.stderr
                }
                
            except FileNotFoundError:
                 return {
                    "success": False, 
                    "output": "", 
                    "error": "Java compiler (javac) not found. Please ensure JDK is installed and in PATH."
                 }
            except Exception as e:
                return {"success": False, "output": "", "error": str(e)}