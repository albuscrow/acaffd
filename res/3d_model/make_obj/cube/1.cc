#include <iostream>
#include <fstream>
#include <cmath>

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
	return os << v.x_ << " " << v.y_ << " " << v.z_;
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
	ofstream fout("cube.obj");

	// 顶点
	V3 v1(1, 1, -1);
	V3 v2(-1, 1, -1);
	V3 v3(-1, -1, -1);
	V3 v4(1, -1, -1);
	V3 v5(1, 1, 1);
	V3 v6(-1, 1, 1);
	V3 v7(-1, -1, 1);
	V3 v8(1, -1, 1);

	fout << "v " << v1 << "\nv " << v2 << "\nv " << v3 << "\nv " << v4 << endl;
	fout << "v " << v5 << "\nv " << v6 << "\nv " << v7 << "\nv " << v8 << endl << endl;

	// 测试用顶点，目的是让整个模型范围扩大，防止调整之后有些顶点跑出原有范围
	double x = 1.4;
	V3 va1(x, x, -x);
	V3 va2(-x, x, -x);
	V3 va3(-x, -x, -x);
	V3 va4(x, -x, -x);
	V3 va5(x, x, x);
	V3 va6(-x, x, x);
	V3 va7(-x, -x, x);
	V3 va8(x, -x, x);

	fout << "v " << va1 << "\nv " << va2 << "\nv " << va3 << "\nv " << va4 << endl;
	fout << "v " << va5 << "\nv " << va6 << "\nv " << va7 << "\nv " << va8 << endl << endl;

	// 法向
	V3 n1(-1, 0, 0);
	V3 n2(1, 0, 0);
	V3 n3(0, -1, 0);
	V3 n4(0, 1, 0);
	V3 n5(0, 0, -1);
	V3 n6(0, 0, 1);

	double face_factor = 1.0, corner_factor = 1.0;
	V3 n12 = n1 * face_factor + v2 * corner_factor;		// 1
	V3 n16 = n1 * face_factor + v6 * corner_factor;		// 2
	V3 n17 = n1 * face_factor + v7 * corner_factor;		// 3
	V3 n13 = n1 * face_factor + v3 * corner_factor;		// 4
	n12.normalize(); n16.normalize(); n17.normalize(); n13.normalize();

	V3 n21 = n2 * face_factor + v1 * corner_factor;		// 5
	V3 n25 = n2 * face_factor + v5 * corner_factor;		// 6
	V3 n28 = n2 * face_factor + v8 * corner_factor;		// 7
	V3 n24 = n2 * face_factor + v4 * corner_factor;		// 8
	n21.normalize(); n25.normalize(); n28.normalize(); n24.normalize();

	V3 n38 = n3 * face_factor + v8 * corner_factor;		// 9
	V3 n37 = n3 * face_factor + v7 * corner_factor;		// 10 
	V3 n33 = n3 * face_factor + v3 * corner_factor;		// 11
	V3 n34 = n3 * face_factor + v4 * corner_factor;		// 12
	n38.normalize(); n37.normalize(); n33.normalize(); n34.normalize();

	V3 n45 = n4 * face_factor + v5 * corner_factor;		// 13
	V3 n46 = n4 * face_factor + v6 * corner_factor;		// 14
	V3 n42 = n4 * face_factor + v2 * corner_factor;		// 15
	V3 n41 = n4 * face_factor + v1 * corner_factor;		// 16
	n45.normalize(); n46.normalize(); n42.normalize(); n41.normalize();

	V3 n51 = n5 * face_factor + v1 * corner_factor;		// 17
	V3 n52 = n5 * face_factor + v2 * corner_factor;		// 18
	V3 n53 = n5 * face_factor + v3 * corner_factor;		// 19
	V3 n54 = n5 * face_factor + v4 * corner_factor;		// 20
	n51.normalize(); n52.normalize(); n53.normalize(); n54.normalize();

	V3 n65 = n6 * face_factor + v5 * corner_factor;		// 21
	V3 n66 = n6 * face_factor + v6 * corner_factor;		// 22
	V3 n67 = n6 * face_factor + v7 * corner_factor;		// 23
	V3 n68 = n6 * face_factor + v8 * corner_factor;		// 24
	n65.normalize(); n66.normalize(); n67.normalize(); n68.normalize();

	// 输出
	fout << "vn " << n12 << "\nvn " << n16 << "\nvn " << n17 << "\nvn " << n13 << endl;
	fout << "vn " << n21 << "\nvn " << n25 << "\nvn " << n28 << "\nvn " << n24 << endl; 
	fout << "vn " << n38 << "\nvn " << n37 << "\nvn " << n33 << "\nvn " << n34 << endl;
	fout << "vn " << n45 << "\nvn " << n46 << "\nvn " << n42 << "\nvn " << n41 << endl;
	fout << "vn " << n51 << "\nvn " << n52 << "\nvn " << n53 << "\nvn " << n54 << endl;
	fout << "vn " << n65 << "\nvn " << n66 << "\nvn " << n67 << "\nvn " << n68 << endl;
	fout << endl;

	fout << "f 2//1 3//4 6//2" << "\nf 6//2 3//4 7//3" << endl;
	fout << "f 1//5 5//6 8//7" << "\nf 1//5 8//7 4//8" << endl;
	fout << "f 8//9 7//10 3//11" << "\nf 8//9 3//11 4//12" << endl;
	fout << "f 1//16 2//15 6//14" << "\nf 1//16 6//14 5//13" << endl;
	fout << "f 4//20 2//18 1//17" << "\nf 4//20 3//19 2//18" << endl;
	fout << "f 5//21 6//22 7//23" << "\nf 5//21 7//23 8//24" << endl;
	//fout << "f 5//21 7//23 8//24" << endl;

	fout.close();
	return 0;
}
