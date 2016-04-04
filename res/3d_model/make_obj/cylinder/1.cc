#include <fstream>
#include <cmath>

using namespace std;

int main()
{
	double scale_x = 2, scale_y = 1, scale_z = 1;
	double scale_x_1 = 1.0 / scale_x;
	double scale_y_1 = 1.0 / scale_y;
	double scale_z_1 = 1.0 / scale_z;

	const double PI = 3.14159265358949323846;
	double h = 1.0, r = 1.0;
	int step = 12;

	ofstream fout("cylinder.obj");
	// 顶点
	for (int i = 0; i < step; ++i)
	{
		double theta = 2 * PI * i / step;
		double z = r * cos(theta) * scale_z;
		double x = r * sin(theta) * scale_x;
		double y = h * scale_y;
		fout << "v " << x << " " << y << " " << z << endl;
		y = -h * scale_y;
		fout << "v " << x << " " << y << " " << z << endl;
	}
	fout << "v " << 0.0 << " " << h * scale_y << " " << 0.0 << endl;
	fout << "v " << 0.0 << " " << -h * scale_y << " " << 0.0 << endl;

	// 法向
	for (int i = 0; i < step; ++i)
	{
		double theta = 2 * PI * i / step;
		double z = cos(theta) * scale_z_1;
		double x = sin(theta) * scale_x_1;
		fout << "vn " << x << " " << 0.0 << " " << z << endl;
	}
	fout << "vn 0 1 0" << endl;
	fout << "vn 0 -1 0" << endl;

	// 面片
	for (int i = 1; i <= step; ++i)
	{
		int i1 = i * 2 - 1;
		int i2 = i * 2;
		int i3 = i * 2 + 1;
		int i4 = i * 2 + 2;
		int iplus1 = i + 1;
		if (i == step)
		{
			i3 = 1;
			i4 = 2;
			iplus1 = 1;
		}
		fout << "f " << i1 << "//" << i	<< " "
					 <<	i2 << "//" << i << " "
					 << i3 << "//" << iplus1 << endl;
		fout << "f " << i3 << "//" << iplus1 << " "
					 << i2 << "//" << i << " "
					 << i4 << "//" << iplus1 << endl;
		fout << "f " << i1 << "//" << step + 1 << " "
					 << i3 << "//" << step + 1 << " "
					 << step * 2 + 1 << "//" << step + 1 << endl;
		fout << "f " << i4 << "//" << step + 2 << " "
					 << i2 << "//" << step + 2 << " "
					 << step * 2 + 2 << "//" << step + 2 << endl;
	}

	fout.close();

	return 0;
}
