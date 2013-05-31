g++ -m32 -Wno-deprecated -O2 -fomit-frame-pointer -shared -D_WIN32 -I /C/Python27/include -L /C/Python27/libs glmod.cpp -lpython27 -lopengl32 -export-all-symbols -o glmod.pyd
