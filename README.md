# huffman_algorithm

Compressed binary string consists of:
1. header:
   a) count of bytes UTF-8 encoded of rest of header
   b) UTF-8 symbols encoded: '0', '1' or symbol
2. sequence to decode

   For Linux:
1. download project
2. cd /path/to/project
3. `python3 -m venv venv` to create python environment
4. `chmod +x ./venv/bin/activate && ./venv/bin/activate`
5. `pip install -r requirements.txt`
6.
   a) `python3 main.py *source_path* *dest_path*` to encode;   
   or   
   b) `python3 main.py decode *source_path* *dest_path*` to decode;




You can check:
`
python3 main.py tests/test_files/test2.xml tests/test_files/test2_enc && 
python3 main.py decode tests/test_files/test2_enc tests/test_files/test2_res && 
rm tests/test_files/test2_enc tests/test_files/test2_res
`
--- 189 different symbols ---
--- 1.7757115364074707 seconds to define symbols frequency ---
--- 3.5352022647857666 seconds to encode file ---
--- 5.336536407470703 seconds to compress file ---
--- Compression: 55.02 % ---
--- 0.11851668357849121 seconds to read all bytes from file ---
--- 7.032465934753418 seconds to decode file and write it to dest ---
--- 7.173500299453735 seconds to decompress ---
--- Compression: 55.02 % ---


`
cat tests/test_files/test2.xml > tests/test_files/test2_tmp.xml && 
cat tests/test_files/test2.xml >> tests/test_files/test2_tmp.xml && 
cat tests/test_files/test2.xml >> tests/test_files/test2_tmp.xml  && 
python3 main.py tests/test_files/test2_tmp.xml tests/test_files/test2_enc && 
python3 main.py decode tests/test_files/test2_enc tests/test_files/test2_res.xml &&
rm tests/test_files/test2_tmp.xml tests/test_files/test2_enc tests/test_files/test2_res.xml
`
--- 189 different symbols ---
--- 5.348633289337158 seconds to define symbols frequency ---
--- 10.284911870956421 seconds to encode file ---
--- 15.673316478729248 seconds to compress file ---
--- Compression: 55.02 % ---
--- 0.35221123695373535 seconds to read all bytes from file ---
--- 21.67078685760498 seconds to decode file and write it to dest ---
--- 22.08542490005493 seconds to decompress ---
--- Compression: 55.02 % ---

