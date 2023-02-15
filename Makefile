pack:
	rm -rf src/temp \\
	pyinstaller --target-arch x86_64 -F src/main.py