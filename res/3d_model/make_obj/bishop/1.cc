#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>

using namespace std;

class V3
{
	double x_, y_, z_;
public:
	V3(double x, double y, double z) { x_ = x; y_ = y; z_ = z; }
	void normalize();
	double norm() const { return sqrt(x_ * x_ + y_ * y_ + z_ * z_); }
	double x() const { return x_; }
	double y() const { return y_; }
	double z() const { return z_; }
	friend const V3 operator+(const V3 &v0, const V3 &v1);
	friend const V3 operator-(const V3 &v0, const V3 &v1);
	friend const V3 operator*(const V3 &v, double k);
	friend ostream &operator<<(ostream &os, const V3 &v);
};

void V3::normalize()
{
	double length_1 = 1.0 / norm();
	x_ *= length_1;
	y_ *= length_1;
	z_ *= length_1;
}

const V3 operator+(const V3 &v0, const V3 &v1)
{
	return V3(v0.x_ + v1.x_, v0.y_ + v1.y_, v0.z_ + v1.z_);
}

const V3 operator-(const V3 &v0, const V3 &v1)
{
	return V3(v0.x_ - v1.x_, v0.y_ - v1.y_, v0.z_ - v1.z_);
}

const V3 operator*(const V3 &v, double k)
{
	return V3(v.x_ * k, v.y_ * k, v.z_ * k);
}

ostream &operator<<(ostream &os, const V3 &v)
{
	return os << "(" << v.x_ << ", " << v.y_ << ", " << v.z_ << ")" << endl;
}

V3 calcNormal(const V3 &v0, const V3 &v1, const V3 &v2)
{
	V3 v01 = v1 - v0;
	V3 v02 = v2 - v0;

	V3 normal(v01.y() * v02.z() - v01.z() * v02.y(),
			  v01.z() * v02.x() - v01.x() * v02.z(),
			  v01.x() * v02.y() - v01.y() * v02.x());
	normal.normalize();
	return normal;
}

int main()
{
// 定义AREA_AVERAGE_NORMAL表示使用顶点一圈面片面积的加权平均，否则直接平均
#define AREA_AVERAGE_NORMAL
#ifdef AREA_AVERAGE_NORMAL
	ofstream fout("biship_cym_area_average_normal.obj");
#else
	ofstream fout("biship_cym_direct_average_normal.obj");
#endif

//#define TEST
#ifndef TEST
	// 每行都代表一圈顶点
	// 0号元素代表和中轴线的距离；1号代表和底面的距离；2号代表是否尖锐边，11
	double c[][3] = {
		{737, 926, 1.0},

		{783, 908, -1.0},
		{777, 875, -1.0},
		{802, 827, 1.0},
		{825, 779, 1.0},
		{837, 738, 1.0},
		{833, 706, 1.0},
		{819, 674, 1.0},
		{801, 649, 1.0},
		{785, 612, 1.0},
		{787, 575, -1.0},
		{836, 553, 1.0},
		{863, 528, -1.0},		// 中间最宽处
		{837, 501, 1.0},
		{787, 473, -1.0},
		{792, 421, 1.0},
		{795, 383, 1.0},
		{803, 332, 1.0},
		{813, 301, 1.0},
		{826, 275, 1.0},
		{842, 253, -1.0},
		{863, 248, -1.0},
		{861, 203, -1.0},
		{900, 172, 1.0},
		{927, 127, -1.0},		// 底座最宽处
		//{913, 104, 1.0},			// ????
		{902, 95, -1.0},
		//{911, 84, 1.0},
		{925, 78, -1.0},		// 底座最窄处

		{737, 78, 1.0},
	};
#else
	double c[][3] = {
		{737, 600, 1.0},

		{913, 104, 1.0},
		{902, 95, -1.0},
		{911, 84, 1.0},
		{925, 78, -1.0},

		{737, 78, 1.0},
	};
#endif

	int line = sizeof(c) / sizeof(double) / 3;
	//cout << line << endl;

	double x_base = c[0][0];
	double y_base = c[line - 1][1];
	for (int i = 0; i < line; ++i)
	{
		c[i][0] -= x_base;
		c[i][1] -= y_base;
	}

	const int AROUND = 8;		// 一圈的采样点数
	const double PI = 3.14159265358979;

	// 生成最顶部的一个顶点
	fout << "v 0 " << c[0][1] << " 0" << endl;
	fout << "vn 0 1 0" << endl;
	int v_base = 1, n_base = 1;		// 表示当前圈之前的顶点和法向数量
	for (int i = 1; i < line - 1; ++i)
	{
		vector<V3> n_buffer;
		for (int j = 0; j < AROUND; ++j)
		{
			int j_pre = (j == 0 ? AROUND - 1 : j - 1);
			int j_next = (j == AROUND - 1 ? 0 : j + 1);
			double angle = PI * 2 * j / AROUND;
			double angle_pre = PI * 2 * j_pre / AROUND;
			double angle_next = PI * 2 * j_next / AROUND;

			V3 v_cur(c[i][0] * sin(angle), c[i][1], c[i][0] * cos(angle));
			fout << "v " << v_cur.x() << " " << v_cur.y() << " " << v_cur.z() << endl;

			V3 v_pre(c[i][0] * sin(angle_pre), c[i][1], c[i][0] * cos(angle_pre));
			V3 v_next(c[i][0] * sin(angle_next), c[i][1], c[i][0] * cos(angle_next));
			V3 v_up(c[i-1][0] * sin(angle), c[i-1][1], c[i-1][0] * cos(angle));
			V3 v_down(c[i+1][0] * sin(angle), c[i+1][1], c[i+1][0] * cos(angle));

#ifdef AREA_AVERAGE_NORMAL
			double h_up = (v_pre - v_cur).norm();
			double h_down = (v_down - v_cur).norm();
#endif

			V3 n_up_pre = calcNormal(v_cur, v_up, v_pre);
			V3 n_pre_down = calcNormal(v_cur, v_pre, v_down);
			V3 n_down_next = calcNormal(v_cur, v_down, v_next);
			V3 n_next_up = calcNormal(v_cur, v_next, v_up);

			if (c[i][2] > -0.1)	// 一圈非尖锐边
			{
#ifdef AREA_AVERAGE_NORMAL
				V3 n = (n_up_pre * h_up + n_pre_down * h_down + n_down_next * h_down + n_next_up * h_up) * (0.5 / (h_up + h_down));
#else
				V3 n = (n_up_pre + n_pre_down + n_down_next + n_next_up) * 0.25;
#endif
				n.normalize();
				fout << "vn " << n.x() << " " << n.y() << " " << n.z() << endl;
			}
			else					// 一圈尖锐边
			{
				V3 n_up = (n_up_pre + n_next_up) * 0.5;
				n_up.normalize();
				V3 n_down = (n_pre_down + n_down_next) * 0.5;
				n_down.normalize();
				fout << "vn " << n_up.x() << " " << n_up.y() << " " << n_up.z() << endl;
				n_buffer.push_back(n_down);
			}

			// 开始生成面片
			if (i == 1)		// 最上面一圈面片
			{
				fout << "f 1//1 "
					 << v_base + j + 1 << "//" << n_base + j + 1 << " "
					 << v_base + j_next + 1 << "//" << n_base + j_next + 1 << endl;
			}
			else			// 除最上面和最下面两圈面片的其余面片
			{
				fout << "f "
					 << v_base + j + 1 << "//" << n_base + j + 1 << " "
					 << v_base + j + 1 - AROUND << "//" << n_base + j + 1 - AROUND << " "
					 << v_base + j_pre + 1 - AROUND << "//" << n_base + j_pre + 1 - AROUND << " "
					 << v_base + j_pre + 1 << "//" << n_base + j_pre + 1 << endl;
			}

		}
		// 计数器增加
		v_base += AROUND;
		n_base += AROUND;
		if (c[i][2] < -0.1)	// 一圈尖锐边
			n_base += AROUND;
		// 将生成的尖锐边的下一圈法向输出
		for (vector<V3>::iterator it = n_buffer.begin(); it != n_buffer.end(); ++it)
			fout << "vn " << it->x() << " " << it->y() << " " << it->z() << endl;
	}

	// 生成最底部的一个顶点
	fout << "v 0 0 0" << endl;
	fout << "vn 0 -1 0" << endl;
	// 生成最底部一圈面片
	for (int j = 0; j < AROUND; ++j)
	{
		int j_pre = (j == 0 ? AROUND - 1 : j - 1);
		// 开始生成面片
		fout << "f " << v_base + 1 << "//" << n_base + 1 << " "
			 << v_base + j - AROUND + 1 << "//" << n_base + j - AROUND + 1 << " "
			 << v_base + j_pre - AROUND + 1 << "//" << n_base + j_pre - AROUND + 1 << endl;
	}

	fout.close();
	fout.clear();

	return 0;
}
