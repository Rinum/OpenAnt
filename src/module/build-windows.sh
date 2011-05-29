gcc -shared -D_WIN32 -I /C/Python26/include -L /C/Python26/libs glmod.c -lpython26 -lopengl32 -export-all-symbols -o glmod.pyd
