#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>

using namespace std;

const double PI = 3.14159265358979;

int main()
{
	double scale_x = 2, scale_y = 3, scale_z = 1;
	//double scale_x = 1, scale_y = 1, scale_z = 1;
	double scale_x_1 = 1.0 / scale_x;
	double scale_y_1 = 1.0 / scale_y;
	double scale_z_1 = 1.0 / scale_z;

	ofstream fout("sphere_cym.obj");
	double r = 1;

	// 顶端和底端两个点
	fout << "v 0 " << r * scale_y << " 0\nvn 0 1 0\n"
		 << "v 0 " << -r * scale_y << " 0\nvn 0 -1 0" << endl;

	//int m = 40, n = 40;
	int m = 12, n = 12;
	//int m = 4, n = 4;

	// 球上除顶端和底端外所有的顶点
	for (int i = 1; i < m; ++i)
	{
		double phi = PI * static_cast<double>(i) / m;
		for (int j = 0; j < n; ++j)
		{
			double theta = 2 * PI * static_cast<double>(j) / n;
			double x = r * sin(phi) * cos(theta);
			double y = r * cos(phi);
			double z = r * sin(phi) * sin(theta);
			fout << "v " << x * scale_x << " " << y * scale_y << " " << z * scale_z << endl;
			fout << "vn " << x * scale_x_1 << " " << y * scale_y_1 << " " << z * scale_z_1 << endl;
		}
	}

	// 球顶端的一圈面片
	for (int j = 0; j < n; ++j)
	{
		int next_idx = j + 1 < n ? j + 1 : 0;
		fout << "f 1//1 " << next_idx + 3 << "//" << next_idx + 3 << " "
			 << j + 3 << "//" << j + 3 << " " << endl;
	}

	// 球底端的一圈面片
	int base = 2 + n * (m - 2);
	for (int j = 0; j < n; ++j)
	{
		int next_idx = j + 1 < n ? j + 1 : 0;
		fout << "f 2//2 " << base + j + 1 << "//" << base + j + 1 << " "
			 << base + next_idx + 1 << "//" << base + next_idx + 1 << endl;
	}

	// 球中间的部分
	for (int i = 1; i <= m - 2; ++i)
	//for (int i = 1; i < 5; ++i)
	{
		int base_upper = 2 + n * (i - 1);
		int base_lower = 2 + n * i;
		for (int j = 0; j < n; ++j)
		{
			int j_plus_1 = j + 1 < n ? j + 1 : 0;
			int upperleft = base_upper + j_plus_1 + 1;
			int upperright = base_upper + j + 1;
			int lowerleft = base_lower + j_plus_1 + 1;
			int lowerright = base_lower + j + 1;
			fout << "f " << upperright << "//" << upperright << " "
						 << upperleft << "//" << upperleft << " "
						 << lowerright << "//" << lowerright << "\n"
				 << "f " << lowerright << "//" << lowerright << " "
						 << upperleft << "//" << upperleft << " "
						 << lowerleft << "//" << lowerleft << endl;
		}
	}

	fout.close();

	return 0;
}
