# huffman_algorithm


1. download project
2. cd /path/to/project
3. `python3 -m venv venv` to create python environment
4. `chmod +x ./venv/bin/activate && ./venv/bin/activate`
5. `pip install -r requirements.txt`
6.                   
   a) `python3 main.py *source_path* *dest_path*` to encode;   
   or   
   b) `python3 main.py decode *source_path* *dest_path*` to decode;


Compressed binary string consists of:
1. count of unique symbols (4 bytes)
2. symbols encoding (4 bytes per symbol)
3. symbol codes (4 bytes per code)
4. sequence 
 

