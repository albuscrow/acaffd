#include <iostream>
#include <fstream>
#include <cmath>

using namespace std;

const double PI = 3.14159265358979;

int main()
{
	double scale_x = 2, scale_y = 3, scale_z = 1;
	double scale_x_1 = 1.0 / scale_x;
	double scale_y_1 = 1.0 / scale_y;
	double scale_z_1 = 1.0 / scale_z;

	//ofstream fout("/home/cym/program/OBJ/simple/torus.obj");
	//ofstream fout("/home/cym/program/OBJ/simple/torus_2.obj");
	ofstream fout("torus.obj");
	double r = 1, R = 3.0;
	/*
	 * small_slice是组成小圆线段的数量，big_slice是组成大圆线段的数量
	 * small_slice和phi相关，big_slice和theta相关
	 */
	int small_slice = 20, big_slice = 40;
	//int small_slice = 3, big_slice = 3;

	/*********************** 生成顶点 ***************************/
	for (int i = 0; i < big_slice; ++i)
	{
		for (int j = 0; j < small_slice; ++j)
		{
			double theta = i * 2 * PI / (double)big_slice;
			double phi = j * 2 * PI / (double)small_slice;
			fout << "v " << (R + r * cos(phi)) * cos(theta) * scale_x << " "
						 << (R + r * cos(phi)) * sin(theta) * scale_y << " "
						 << r * sin(phi) * scale_z << endl;
			double centerx = R * cos(theta);
			double centery = R * sin(theta);
			//double centerz = 0;
			double nx = (R + r * cos(phi)) * cos(theta) - centerx;
			double ny = (R + r * cos(phi)) * sin(theta) - centery;
			double nz = r * sin(phi);
			double length = sqrt(nx * nx + ny * ny + nz * nz);
			fout << "vn " << nx / length * scale_x_1 << " " << ny / length * scale_y_1
				 <<   " " << nz / length * scale_z_1 << endl;
		}
	}

	/*********************** 生成面片 ***************************/
	for (int i = 0; i < big_slice; ++i)
	{
		for (int j = 0; j < small_slice; ++j)
		{
			int small_circle_idx = i;
			int small_circle_idx_next = i + 1 < big_slice ? i + 1 : 0;
			int local_idx = j;
			int local_idx_next = j + 1 < small_slice ? j + 1: 0;
			int lowerleft = small_circle_idx * small_slice + local_idx + 1;
			int upperleft = small_circle_idx * small_slice + local_idx_next + 1;
			int lowerright = small_circle_idx_next * small_slice + local_idx + 1;
			int upperright = small_circle_idx_next * small_slice + local_idx_next + 1;
			fout << "f " << upperleft << "//" << upperleft
				 << " " << lowerleft << "//" << lowerleft
				 << " " << lowerright << "//" << lowerright << endl;
			fout << "f " << upperleft << "//" << upperleft
				 << " " << lowerright << "//" << lowerright
				 << " " << upperright << "//" << upperright << endl;
		}
	}

	fout.close();

	return 0;
}
