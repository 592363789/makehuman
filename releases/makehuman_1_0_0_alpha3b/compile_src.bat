gcc -g -Wall -o makehuman ./src/main.c ./src/glmodule.c ./src/core.c ./include/core.h ./include/glmodule.h -Ic:/Python26/include -Ic:/MinGW/include/SDL -I./include -Lc:/Python26/libs -lpython26 -lmingw32 -lSDLmain -lSDL -mconsole -lglu32 -lopengl32 -lgdi32 -lmsvcrt -lwinmm
