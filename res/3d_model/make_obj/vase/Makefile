1 : 1.o obj_data.o
	clang++ 1.o obj_data.o -o 1
1.o: 1.cc obj_data.h
	clang++ -c 1.cc
obj_data.o : obj_data.cc obj_data.h obj_data.inl
	clang++ -c obj_data.cc
