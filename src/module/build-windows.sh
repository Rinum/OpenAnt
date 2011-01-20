gcc -shared -D_WIN32 -I /C/Python27/include -L /C/Python27/libs glmod.c -lpython27 -lopengl32 -export-all-symbols -o glmod.pyd
