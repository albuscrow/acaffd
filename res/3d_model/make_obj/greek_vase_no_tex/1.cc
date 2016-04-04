#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include <vector>
#include <string>

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
	ofstream fout("greek_vase_cym_area_average_normal.obj");
#else
	ofstream fout("greek_vase_cym_direct_average_normal.obj");
#endif

	const int CIRCLE = 16;		// 一圈的采样点数
	const double PI = 3.14159265358979;

	// 每行都代表一圈顶点
	// 0号元素代表和中轴线的距离；1号代表和底面的距离；2号代表是否尖锐边
	double c[][4] = {
		{ 742, 319, 1.0, CIRCLE + 2},
		{ 780, 319, 1.0, CIRCLE + 2},

		{ 846, 319, -1.0, CIRCLE + 2},
		{ 901, 598, -1.0, CIRCLE + 2},
		{ 870, 650, -1.0, CIRCLE + 2},
		{ 916, 820, -1.0, CIRCLE + 2},		// 罐口内沿

		{ 949, 820, -1.0, CIRCLE},			// 罐口外延
		{ 905, 678, 1.0, CIRCLE},
		{ 912, 634, 1.0, CIRCLE},			// 可以注释以便测试
		{ 949, 592, 1.0, CIRCLE},			// 可以注释以便测试
		{ 950, 492, 1.0, CIRCLE},
		{ 920, 392, 1.0, CIRCLE},
		{ 860, 302, 1.0, CIRCLE},
		{ 821, 266, -1.0, CIRCLE},
		{ 819, 246, -1.0, CIRCLE},
		{ 845, 232, 1.0, CIRCLE},
		{ 866, 212, 1.0, CIRCLE},
		{ 876, 187, -1.0, CIRCLE},

		{ 800, 187, 1.0, CIRCLE},
		{ 742, 187, 1.0, CIRCLE},
	};

	int line = sizeof(c) / sizeof(double) / 4;

	double x_base = c[0][0];
	double y_base = c[line - 1][1];
	for (int i = 0; i < line; ++i)
	{
		c[i][0] -= x_base;
		c[i][1] -= y_base;
	}

	cout << "line " << line << endl;
	for (int i = 0; i < line; ++i)
		cout << c[i][0] << ", " << c[i][1] << endl;

	double *tex_y = new double[line];
	double length0 = 0.0, length1 = 0.0;

	int border = -1;
	for (int i = 1; i < line; ++i)
		if (c[i][3] != c[i - 1][3])
		{
			border = i;
			break;
		}
	for (int i = 0; i < border; ++i)
	{
		double delta_x = c[i][0] - c[i + 1][0];
		double delta_y = c[i][1] - c[i + 1][1];
		length0 += sqrt(delta_x * delta_x + delta_y * delta_y);
	}
	for (int i = border; i < line - 1; ++i)
	{
		double delta_x = c[i][0] - c[i + 1][0];
		double delta_y = c[i][1] - c[i + 1][1];
		length1 += sqrt(delta_x * delta_x + delta_y * delta_y);
	}

	double temp_length = 0.0;
	for (int i = 0; i < border; ++i)
	{
		tex_y[i] = temp_length / length0;
		double delta_x = c[i][0] - c[i + 1][0];
		double delta_y = c[i][1] - c[i + 1][1];
		temp_length += sqrt(delta_x * delta_x + delta_y * delta_y);
	}
	temp_length = 0.0;
	for (int i = border; i < line; ++i)
	{
		tex_y[i] = 1.0 - temp_length / length1;
		if (i != line - 1)
		{
			double delta_x = c[i][0] - c[i + 1][0];
			double delta_y = c[i][1] - c[i + 1][1];
			temp_length += sqrt(delta_x * delta_x + delta_y * delta_y);
		}
	}
	cout << endl;
	for (int i = 0; i < line; ++i)
		cout << tex_y[i] << endl;

	fout << "mtllib vase.mtl" << endl;
	fout << "usemtl vase" << endl;
	// 生成最顶部的一个顶点（其实是壶肚内底面中心的一点）
	fout << "v 0 " << c[0][1] << " 0" << endl;
	fout << "vn 0 1 0" << endl;
	for (int j = 0; j <= c[0][3]; ++j)
	{
		double angle = (double)j / c[0][3];
		fout << "vt " << angle << " 0.0" << endl;
	}

	for (int i = 1; i < line - 1; ++i)
	{
		vector<V3> n_buffer;
		vector<double> tex_buffer;
		const int AROUND = c[i][3];
		for (int j = 0; j < AROUND; ++j)
		{
			int j_pre = (j == 0 ? AROUND - 1 : j - 1);
			int j_next = (j == AROUND - 1 ? 0 : j + 1);
			double angle = PI * 2 * j / AROUND;
			double angle_pre = PI * 2 * j_pre / AROUND;
			double angle_next = PI * 2 * j_next / AROUND;

			V3 v_cur(c[i][0] * cos(angle), c[i][1], c[i][0] * sin(angle));
			fout << "v " << v_cur.x() << " " << v_cur.y() << " " << v_cur.z() << endl;
			if (i <= border)
				fout << "vt " << angle / (2 * PI) << " " << tex_y[i] << endl;
			else
				fout << "vt " << 1.0 - angle / (2 * PI) << " " << tex_y[i] << endl;
			if (i == border)
				tex_buffer.push_back(1.0 - angle / (2 * PI));
			if (j == AROUND - 1)
			{
				if (i <= border)
					fout << "vt " << 1.0 << " " << tex_y[i] << endl;
				else
					fout << "vt " << 0.0 << " " << tex_y[i] << endl;
				if (i == border)
					tex_buffer.push_back(0.0);
			}

			V3 v_pre(c[i][0] * cos(angle_pre), c[i][1], c[i][0] * sin(angle_pre));
			V3 v_next(c[i][0] * cos(angle_next), c[i][1], c[i][0] * sin(angle_next));
			V3 v_up(c[i-1][0] * cos(angle), c[i-1][1], c[i-1][0] * sin(angle));
			V3 v_down(c[i+1][0] * cos(angle), c[i+1][1], c[i+1][0] * sin(angle));

#ifdef AREA_AVERAGE_NORMAL
			double h_up = (v_pre - v_cur).norm();
			double h_down = (v_down - v_cur).norm();
#endif

			V3 n_pre_up = calcNormal(v_cur, v_pre, v_up);
			V3 n_down_pre = calcNormal(v_cur, v_down, v_pre);
			V3 n_next_down = calcNormal(v_cur, v_next, v_down);
			V3 n_up_next = calcNormal(v_cur, v_up, v_next);

			if (c[i][2] > -0.1)	// 一圈非尖锐边
			{
#ifdef AREA_AVERAGE_NORMAL
				V3 n = (n_pre_up * h_up + n_down_pre * h_down + n_next_down * h_down + n_up_next * h_up) * (0.5 / (h_up + h_down));
#else
				V3 n = (n_up_pre + n_pre_down + n_down_next + n_next_up) * 0.25;
#endif
				n.normalize();
				fout << "vn " << n.x() << " " << n.y() << " " << n.z() << endl;
			}
			else					// 一圈尖锐边
			{
				V3 n_up = (n_pre_up + n_up_next) * 0.5;
				n_up.normalize();
				V3 n_down = (n_down_pre + n_next_down) * 0.5;
				n_down.normalize();
				fout << "vn " << n_up.x() << " " << n_up.y() << " " << n_up.z() << endl;
				n_buffer.push_back(n_down);
			}
		}
		// 将生成的尖锐边的下一圈法向输出
		for (vector<V3>::iterator it = n_buffer.begin(); it != n_buffer.end(); ++it)
			fout << "vn " << it->x() << " " << it->y() << " " << it->z() << endl;
		for (vector<double>::iterator it = tex_buffer.begin(); it != tex_buffer.end(); ++it)
			fout << "vt " << *it << " " << tex_y[i] << endl;
	}
	// 生成最底部的一个顶点
	fout << "v 0 0 0" << endl;
	fout << "vn 0 -1 0" << endl;
	//for (int j = 0; j <= c[line - 1][3]; ++j)
	for (int j = 0; j < c[line - 1][3]; ++j)
	{
		double angle = 1.0 - (double)j / c[line - 1][3];
		fout << "vt " << angle << " 0.0" << endl;
	}

	// 开始生成面片
	int v_base = 1, t_base = c[0][3] + 1, n_base = 1;		// 表示当前圈之前的顶点、纹理、法向数量
	for (int i = 1; i < line - 1; ++i)
	{
		const int AROUND = c[i][3];
		const int AROUND_PRE = c[i - 1][3];
		for (int j = 0; j < AROUND; ++j)
		{
			int j_next = (j == AROUND - 1 ? 0 : j + 1);
			if (i == 1)		// 最上面一圈面片
			{
				fout << "f 1" << "/"
					 << t_base - AROUND_PRE - 1 + j + 1 << "/"
					 << "1" << " "

					 << v_base + j_next + 1 << "/"
					 << t_base + j + 1 + 1 << "/"
					 << n_base + j_next + 1 << " "

					 << v_base + j + 1 << "/"
					 << t_base + j + 1 << "/"
					 << n_base + j + 1 << endl;
			}
			else			// 除最上面和最下面两圈面片的其余面片
			{
				if (c[i][3] == c[i - 1][3])
				{
					fout << "f "
						 << v_base + j + 1 << "/"
						 << t_base + j + 1 << "/"
						 << n_base + j + 1 << " "

						 << v_base + j + 1 - AROUND << "/"
						 << t_base + j + 1 - AROUND - 1 << "/"
						 << n_base + j + 1 - AROUND << " "

						 << v_base + j_next + 1 - AROUND << "/"
						 << t_base + j + 1 + 1 - AROUND - 1 << "/"
						 << n_base + j_next + 1 - AROUND << " "

						 << v_base + j_next + 1 << "/"
						 << t_base + j + 1 + 1 << "/"
						 << n_base + j_next + 1 << endl;
				}
				else
				{
					if (j <= 3)
					{
						fout << "f "
							 << v_base + j + 1 << "/"
							 << t_base + j + 1 << "/"
							 << n_base + j + 1 << " "

							 << v_base - AROUND_PRE + j + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 1 << "/"
							 << n_base - AROUND_PRE + j + 1 << " "

							 << v_base - AROUND_PRE + j_next + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 1 + 1 << "/"
							 << n_base - AROUND_PRE + j_next + 1 << endl;

						fout << "f "
							 << v_base + j + 1 << "/"
							 << t_base + j + 1 << "/"
							 << n_base + j + 1 << " "

							 << v_base - AROUND_PRE + j_next + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 1 + 1 << "/"
							 << n_base - AROUND_PRE + j_next + 1 << " "

							 << v_base + j_next + 1 << "/"
							 << t_base + j + 1 + 1 << "/"
							 << n_base + j_next + 1 << endl;
					}
					else if (j <= 7)
					{
						fout << "f "
							 << v_base + j_next + 1 << "/"
							 << t_base + j + 1 + 1 << "/"
							 << n_base + j_next + 1 << " "

							 << v_base + j + 1 << "/"
							 << t_base + j + 1 << "/"
							 << n_base + j + 1 << " "

							 << v_base - AROUND_PRE + j + 1 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 1 + 1 << "/"
							 << n_base - AROUND_PRE + j + 1 + 1 << " "

							 << v_base - AROUND_PRE + j + 2 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 2 + 1 << "/"
							 << n_base - AROUND_PRE + j + 2 + 1 << endl;
					}
					else if (j <= 11)
					{
						fout << "f "
							 << v_base + j_next + 1 << "/"
							 << t_base + j + 1 + 1 << "/"
							 << n_base + j_next + 1 << " "

							 << v_base + j + 1 << "/"
							 << t_base + j + 1 << "/"
							 << n_base + j + 1 << " "

							 << v_base - AROUND_PRE + j + 2 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 2 + 1 << "/"
							 << n_base - AROUND_PRE + j + 2 + 1 << endl;

						fout << "f "
							 << v_base + j + 1 << "/"
							 << t_base + j + 1 << "/"
							 << n_base + j + 1 << " "

							 << v_base - AROUND_PRE + j + 1 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 1 + 1 << "/"
							 << n_base - AROUND_PRE + j + 1 + 1 << " "

							 << v_base - AROUND_PRE + j + 2 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 2 + 1 << "/"
							 << n_base - AROUND_PRE + j + 2 + 1 << endl;
					}
					else
					{
						int j_up_next = (j == AROUND - 1 ? 0 : j + 3);
						fout << "f "
							 << v_base + j_next + 1 << "/"
							 << t_base + j + 1 + 1 << "/"
							 << n_base + j_next + 1 << " "

							 << v_base + j + 1 << "/"
							 << t_base + j + 1 << "/"
							 << n_base + j + 1 << " "

							 << v_base - AROUND_PRE + j + 2 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 2 + 1 << "/"
							 << n_base - AROUND_PRE + j + 2 + 1 << " "

							 << v_base - AROUND_PRE + j_up_next + 1 << "/"
							 << t_base - AROUND_PRE - 1 + j + 3 + 1 << "/"
							 << n_base - AROUND_PRE + j_up_next + 1 << endl;
					}
					if (j == 4)				// 生成三角面片
					{
						fout << "f "
							 << v_base + 4 + 1 << "/"
							 << t_base + 4 + 1 << "/"
							 << n_base + 4 + 1 << " "

							 << v_base - AROUND_PRE + 4 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + 4 + 1 << "/"
							 << n_base - AROUND_PRE + 4 + 1 << " "

							 << v_base - AROUND_PRE + 5 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + 5 + 1 << "/"
							 << n_base - AROUND_PRE + 5 + 1 << endl;
					}
					else if (j == 12)		// 生成三角面片
					{
						fout << "f "
							 << v_base + 12 + 1 << "/"
							 << t_base + 12 + 1 << "/"
							 << n_base + 12 + 1 << " "

							 << v_base - AROUND_PRE + 13 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + 13 + 1 << "/"
							 << n_base - AROUND_PRE + 13 + 1 << " "

							 << v_base - AROUND_PRE + 14 + 1 << "/"
							 << t_base - AROUND_PRE - 1 + 14 + 1 << "/"
							 << n_base - AROUND_PRE + 14 + 1 << endl;
					}
				}
			}
		}
		// 计数器增加
		v_base += AROUND;
		t_base += (AROUND + 1);
		n_base += AROUND;
		if (c[i][2] < -0.1)	// 一圈尖锐边
			n_base += AROUND;
		if (i == border)
			t_base += (AROUND + 1);
	}

	// 生成最底部一圈面片
	const int AROUND = c[line - 1][3];
	for (int j = 0; j < AROUND; ++j)
	{
		int j_next = (j == AROUND - 1 ? 0 : j + 1);
		// 开始生成面片
		fout << "f "
			 << v_base + 1 << "/"
			 << t_base + j + 1 << "/"
			 << n_base + 1 << " "

			 << v_base + j - AROUND + 1 << "/"
			 << t_base + j - AROUND - 1 + 1 << "/"
			 << n_base + j - AROUND + 1 << " "

			 << v_base + j_next - AROUND + 1 << "/"
			 << t_base + j + 1 - AROUND - 1 + 1 << "/"
			 << n_base + j_next - AROUND + 1 << endl;
	}

	/*============================ 加上把手 ==============================*/
	++v_base;
	t_base += c[line - 1][3];
	++n_base;
	cout << "v_base = " << v_base <<  endl;
	cout << "t_base = " << t_base <<  endl;
	cout << "n_base = " << n_base <<  endl;

	ifstream fin("handle.obj");
	string line_in;
	//int counter = 0;
	while(getline(fin, line_in))
	{
		istringstream iss(line_in);
		string primitive;
		iss >> primitive;
		if (primitive == "v")
		{
			double x, y, z;
			iss >> x >> y >> z;
			double factor = 5.6;
			double y_max = 53.95;
			//double factor = 4.0 / 1000;
			//double y_max = 249000;
			x *= factor;
			y *= factor;
			y_max *= factor;
			z *= factor;
			double y_delta = 800 - y_base - y_max;
			y += y_delta;
			//fout << "v " << x << " " << y << " " << z << endl;
			fout << "v " << -z << " " << y << " " << x << endl;
		}
		else if (primitive == "vn")
		{
			double x, y, z;
			iss >> x >> y >> z;
			fout << "vn " << -z << " " << y << " " << x << endl;
		}
		else if (primitive == "vt")
			fout << line_in << endl;
		else if (primitive == "f")
		{
			//counter++;
			//if (counter == 44)
				//break;
			int v_id, t_id, n_id;
			char slash0, slash1;
			fout << "f ";
			while(iss >> v_id >> slash0 >> t_id >> slash1 >> n_id)
			{
				fout << v_id + v_base << "/"
					 << t_id + t_base << "/"
					 << n_id + n_base << " ";
			}
			fout << endl;
		}
	}
	fin.close();
	fin.clear();

	fout.close();
	fout.clear();
	return 0;
}
