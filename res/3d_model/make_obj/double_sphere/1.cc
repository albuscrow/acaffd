#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>

using namespace std;

int main()
{
	const double PI = 3.14159265358979;

	ofstream fout("double_sphere_cym.obj");
	double r0 = 2, r1 = 7;			// 上下两个球的半径
	double l0 = 0.2;				// 0号球向上移动的距离，要保证小于r0
	double scale_x = 2, scale_y = 1, scale_z = 1;
	double scale_x_1 = 1.0 / scale_x;
	double scale_y_1 = 1.0 / scale_y;
	double scale_z_1 = 1.0 / scale_z;
	try
	{
		if (l0 >= r0)
		{
			ostringstream oss;
			oss << "l0 >= r0, l0最多" << r0;
			throw oss.str();
		}
	}
	catch (const string &msg)
	{
		cerr << msg << endl;
		fout.close();
		return 1;
	}

	// 1号球向下移动的距离，此距离可以保证两球的交线在 y = 0 平面上
	try
	{
		if (r1 * r1 <= r0 * r0 - l0 * l0)
		{
			double r1_least = sqrt(r0 * r0 - l0 * l0);
			ostringstream oss;
			oss << "两球无法相交，r1至少要" << r1_least;
			throw oss.str();
		}
	}
	catch (const string &msg)
	{
		cerr << msg << endl;
		fout.close();
		return 1;
	}

	double l1 = -sqrt(r1 * r1 - (r0 * r0 - l0 * l0));
	cout << "r = " << sqrt(r0 * r0 - l0 * l0) << endl;
	cout << "l1 = " << l1 << endl;
	cout << "result0 = " << l0 / sqrt(r0 * r0 - l0 * l0) << endl;
	cout << "result1 = " << l1 / sqrt(r0 * r0 - l0 * l0) << endl;

	double phi0 = acos(l0 / r0);
	double phi1 = acos(-l1 / r1);

	int step = 12;					// 圆周采样点数量
	int level = 10;					// y方向面片数量
	//int step = 4;					// 圆周采样点数量
	//int level = 4;					// y方向面片数量

	// 1号球的上半部分顶点，包括交界点，不包括最顶端的顶点，生成方向从上到下
	for (int i = 1; i <= level; ++i)
	{
		double phi = phi1 * static_cast<double>(i) / level;
		for (int j = 0; j < step; ++j)
		{
			double theta = 2 * PI * static_cast<double>(j) / step;
			double x = r1 * sin(phi) * cos(theta);
			double y = r1 * cos(phi) + l1;
			double z = r1 * sin(phi) * sin(theta);
			fout << "v " << x * scale_x << " " << y * scale_y << " " << z * scale_z << endl;
#define NORMALIZE
#ifdef NORMALIZE
			double yy = y - l1;
			double length = sqrt(x * x + yy * yy + z * z);
			fout << "vn " << x / length * scale_x_1<< " "
				<< (y - l1) / length * scale_y_1 << " "
				<< z / length * scale_z_1 << endl;
#else
			fout << "vn " << x * scale_x_1 << " " << (y - l1) * scale_y_1
				 << " " << z * scale_z_1 << endl;
#endif
		}
	}

	// 0号球的下半部分顶点，不包括交界顶点和最底端的顶点，但是包括交界点的法向，生成方向从上到下
	for (int i = 0; i <= level - 1; ++i)
	{
		double phi = PI - phi0 + phi0 * static_cast<double>(i) / level;
		for (int j = 0; j < step; ++j)
		{
			double theta = 2 * PI * static_cast<double>(j) / step;
			double x = r0 * sin(phi) * cos(theta);
			double y = r0 * cos(phi) + l0;
			double z = r0 * sin(phi) * sin(theta);
			if (i != 0)
				fout << "v " << x * scale_x << " " << y * scale_y << " " << z * scale_z << endl;
#ifdef NORMLAIZE
			double yy = y - l0;
			double length = sqrt(x * x + yy * yy + z * z);
			fout << "vn " << x / length * scale_x_1<< " "
				<< (y - l0) / length * scale_y_1 << " "
				<< z / length * scalle_z_1 << endl;
#else
			fout << "vn " << x * scale_x_1 << " " << (y - l0) * scale_y_1
				 << " " << z * scale_z_1 << endl;
#endif
		}
	}

	//fout << "v 0 " << r1 + l1 << " 0\nvn 0 1 0" << endl;	// 1号球最上面的顶点
	//fout << "v 0 " << -r0 + l0 << " 0\nvn 0 -1 0" << endl;	// 0号球最下面的顶点
	fout << "v 0 " << (r1 + l1) * scale_y << " 0\nvn 0 1 0" << endl;	// 1号球最上面的顶点
	fout << "v 0 " << (-r0 + l0) * scale_y << " 0\nvn 0 -1 0" << endl;	// 0号球最下面的顶点

	/******************************************************************************/
	/******************************************************************************/
	/******************************************************************************/
	/******************************************************************************/

	// 1号球除顶端一圈面片的其余部分
	for (int i = 1; i <= level - 1; ++i)
	//for (int i = 1; i <= 1; ++i)
	{
		int base_upper = step * (i - 1);
		int base_lower = step * i;
		for (int j = 0; j < step; ++j)
		{
			int j_plus_1 = j + 1 < step ? j + 1 : 0;
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
	// 1号球顶端一圈面片
	for (int j = 0; j < step; ++j)
	{
		int next_idx = j + 1 < step ? j + 1 : 0;
		fout << "f " << 1 + step * (2 * level - 1) << "//" << 1 + step * (2 * level) << " "
			 << next_idx + 1 << "//" << next_idx + 1 << " "
			 << j + 1 << "//" << j + 1 << endl;
	}

	// 0号球除最下面一圈面片的其余部分
	for (int i = 1; i <= level - 1; ++i)
	//for (int i = level - 1; i <= level - 1; ++i)
	{
		int base_upper = step * (i - 1) + step * (level - 1);
		int base_lower = step * i + step * (level - 1);
		for (int j = 0; j < step; ++j)
		{
			int j_plus_1 = j + 1 < step ? j + 1 : 0;
			int upperleft = base_upper + j_plus_1 + 1;
			int upperright = base_upper + j + 1;
			int lowerleft = base_lower + j_plus_1 + 1;
			int lowerright = base_lower + j + 1;
			fout << "f " << upperright << "//" << upperright + step << " "
						 << upperleft << "//" << upperleft + step << " "
						 << lowerright << "//" << lowerright + step << "\n"
				 << "f " << lowerright << "//" << lowerright + step << " "
						 << upperleft << "//" << upperleft + step << " "
						 << lowerleft << "//" << lowerleft + step << endl;
		}
	}
	// 0号球底端一圈面片
	int v_base = step * (2 * level - 2);
	int n_base = step * (2 * level - 1);
	for (int j = 0; j < step; ++j)
	{
		int next_idx = j + 1 < step ? j + 1 : 0;
		fout << "f " << 2 + v_base + step << "//" << 2 + n_base + step << " "
			 << v_base + j + 1 << "//" << n_base + j + 1 << " "
			 << v_base + next_idx + 1 << "//" << n_base + next_idx + 1 << endl;
	}

	// 测试用
	//fout << "v 0 " << 1.3 << "0\nvn 0 1 0" << endl;
	//fout << "v 0 " << -1.3 << "0\nvn 0 1 0" << endl;
	fout.close();

	return 0;
}
