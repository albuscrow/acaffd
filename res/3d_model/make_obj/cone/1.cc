#include <fstream>
#include <cmath>

using namespace std;

int main()
{
	double scale_x = 2, scale_y = 3, scale_z = 1;
	double scale_x_1 = 1.0 / scale_x;
	double scale_y_1 = 1.0 / scale_y;
	double scale_z_1 = 1.0 / scale_z;

	const double PI = 3.14159265358949323846;
	double h = 0.8;			// 圆台高度的一半
	double r_upper = 0.5;	// 上底面半径
	double r_lower = 1.0;	// 下底面半径
	int step = 12;			// 圆周一圈采样点个数
	int level = 8;			// 从上之下有多少层面片，至少1
	//int level = 1;			// 从上之下有多少层面片，至少1

	ofstream fout("cone_cym.obj");

	// 顶点
	for (int i = 0; i < step; ++i)				// 圆周不同位置
	{
		double theta = 2 * PI * i / step;
		for (int j = 0; j <= level; ++j)			// 从上到下不同层
		{
			double r = (r_upper * (level - j) + r_lower * j) / level;
			double x = r * cos(theta) * scale_x;
			double y = (h * (level - j) - h * j) / level * scale_y;
			double z = r * sin(theta) * scale_z;
			fout << "v " << x << " " << y << " " << z << endl;
		}
	}
	fout << "v " << 0.0 << " " << h * scale_y << " " << 0.0 << endl;
	fout << "v " << 0.0 << " " << -h * scale_y << " " << 0.0 << endl;

	// 法向
	double h_small = r_lower * (r_lower - r_upper) / (2 * h) * scale_y_1;
	for (int i = 0; i < step; ++i)			// 圆周不同位置
	{
		double theta = 2 * PI * i / step;
		double x = r_lower * cos(theta) * scale_x_1;
		double z = r_lower * sin(theta) * scale_z_1;
		fout << "vn " << x << " " << h_small << " " << z << endl;
	}
	fout << "vn 0 1 0" << endl;
	fout << "vn 0 -1 0" << endl;

	// 面片
	for (int i = 1; i <= step; ++i)
	{
		int next_n_id = i + 1;
		if (i == step)
			next_n_id = 1;
		for (int j = 0; j < level; ++j)
		{
			int current_v_upper = (i - 1) * (level + 1) + (j + 1);
			int current_v_lower = (i - 1) * (level + 1) + (j + 2);

			int next_v_upper = i * (level + 1) + (j + 1);
			if (i == step)
				next_v_upper = j + 1;

			int next_v_lower = i * (level + 1) + (j + 2);
			if (i == step)
				next_v_lower = j + 2;

			// 侧面
			fout << "f " << current_v_upper << "//" << i << " "
						 <<	next_v_upper << "//" << next_n_id << " "
						 << next_v_lower << "//" << next_n_id << endl;
			fout << "f " << current_v_upper << "//" << i << " "
						 <<	next_v_lower << "//" << next_n_id << " "
						 << current_v_lower << "//" << i << endl;
		}

		// 上底面
		int current_v = (i - 1) * (level + 1) + 1;
		int next_v = i * (level + 1) + 1;
		if (i == step)
			next_v = 1;
		fout << "f " << step * (level + 1) + 1 << "//" << step + 1 << " "
					 << next_v << "//" << step + 1 << " "
					 << current_v << "//" << step + 1 << endl;
		// 下底面
		current_v = (i - 1) * (level + 1) + level + 1;
		next_v = i * (level + 1) + level + 1;
		if (i == step)
			next_v = level + 1;
		fout << "f " << step * (level + 1) + 2 << "//" << step + 2 << " "
					 << current_v << "//" << step + 2 << " "
					 << next_v << "//" << step + 2 << endl;
	}

	fout.close();

	return 0;
}
