#include <iostream>
#include <fstream>
#include <vector>
#include "matrix_stack.h"

using namespace std;

int main()
{
	using namespace matrix_stack;

	ModelViewMatrixStack modelViewMatrixStack;
	ModelViewMatrixStack cubeMapMatrixStack;
	vector<Vector4> ctrl_points0, ctrl_points1, ctrl_points2, ctrl_points3;
	int cp_num_x = 5, cp_num_y = 9, cp_num_z = 5;

	double min_y = 999999;
	ifstream fin0("step0.edit"), fin1("step1.edit"), fin2("step2.edit"), fin3("step3.edit");
	for (int i = 0; i < cp_num_x * cp_num_y * cp_num_z; ++i)
	{
		double x, y, z;
		fin0 >> x >> y >> z;
		ctrl_points0.push_back(Vector4(x, y, z));

		fin1 >> x >> y >> z;
		ctrl_points1.push_back(Vector4(x, y, z));
		if (y < min_y)
			min_y = y;

		fin2 >> x >> y >> z;
		ctrl_points2.push_back(Vector4(x, y, z));

		fin3 >> x >> y >> z;
		ctrl_points3.push_back(Vector4(x, y, z));
	}
	fin1.close(); fin1.clear(); fin2.close(); fin2.clear(); fin3.close(); fin3.clear();

	/*----------------------------------------------------*/

	//double angle = 15;
	int step = 10;

	double cubemap_rot_degree = -0.15;
	double v0 = 5.0, g = 9.8, t = v0 / g;
	ofstream fout("output.target");

	// 棋子到人形静止
	for (int s = 0; s < step; ++s)
	{
		modelViewMatrixStack.loadIdentity();
		//modelViewMatrixStack.translate(0, min_y, 0);
		//modelViewMatrixStack.rotate(180 * s / (step - 1), 0, 1, 0);
		//modelViewMatrixStack.translate(0, -min_y, 0);
		Matrix4x4 top;
		modelViewMatrixStack.top(top);
		double rate1 = (double)s / step;
		double rate0 = 1.0 - rate1;
		fout << "控制顶点 " << 2 << " " << cp_num_x * cp_num_y * cp_num_z << endl;
		for (vector<Vector4>::size_type c = 0; c != ctrl_points0.size(); ++c)
		{
			Vector4 p = ctrl_points0[c] * rate0 + ctrl_points1[c] * rate1;
			double result[3] = {0.0};
			for (int i = 0; i < 3; ++i)
				for (int j = 0; j < 4; ++j)
					result[i] += top[j][i] * p[j];
			//fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
			double k = t * (double)s / (step - 1);
			//fout << "\t" << p[0] << " " << p[1] + v0 * k - 0.5 * g * k * k << " " << p[2] << endl;
			//fout << "\t" << result[0] << " " << result[1] + v0 * k - 0.5 * g * k * k << " " << result[2] << endl;
			fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
		}

		// cubemap旋转矩阵
		fout << "cubemap" << endl << "\t";
		cubeMapMatrixStack.loadIdentity();
		//cubeMapMatrixStack.rotate(0, 0, 1, 0);
		cubeMapMatrixStack.top(top);
		for (int i = 0; i < 4; ++i)
			for (int j = 0; j < 4; ++j)
				fout << top[i][j] << " ";
		fout << endl;
	}

	// 静止到迈左脚
	for (int s = 0; s < step; ++s)
	{
		modelViewMatrixStack.loadIdentity();
		//modelViewMatrixStack.translate(0, min_y, 0);
		//modelViewMatrixStack.rotate(180 * s / (step - 1), 0, 1, 0);
		//modelViewMatrixStack.translate(0, -min_y, 0);
		Matrix4x4 top;
		modelViewMatrixStack.top(top);
		double rate1 = (double)s / step;
		double rate0 = 1.0 - rate1;
		fout << "控制顶点 " << 2 << " " << cp_num_x * cp_num_y * cp_num_z << endl;
		for (vector<Vector4>::size_type c = 0; c != ctrl_points1.size(); ++c)
		{
			Vector4 p = ctrl_points1[c] * rate0 + ctrl_points2[c] * rate1;
			double result[3] = {0.0};
			for (int i = 0; i < 3; ++i)
				for (int j = 0; j < 4; ++j)
					result[i] += top[j][i] * p[j];
			//fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
			double k = t * (double)s / (step - 1);
			//fout << "\t" << p[0] << " " << p[1] + v0 * k - 0.5 * g * k * k << " " << p[2] << endl;
			//fout << "\t" << result[0] << " " << result[1] + v0 * k - 0.5 * g * k * k << " " << result[2] << endl;
			fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
		}

		// cubemap旋转矩阵
		fout << "cubemap" << endl << "\t";
		cubeMapMatrixStack.loadIdentity();
		cubeMapMatrixStack.rotate(cubemap_rot_degree, 0, 1, 0);
		cubeMapMatrixStack.top(top);
		for (int i = 0; i < 4; ++i)
			for (int j = 0; j < 4; ++j)
				fout << top[i][j] << " ";
		fout << endl;
	}

	// 迈左脚到静止
	for (int s = 0; s < step; ++s)
	{
		modelViewMatrixStack.loadIdentity();
		//modelViewMatrixStack.translate(0, min_y, 0);
		//modelViewMatrixStack.rotate(-180 * s / step, 0, 1, 0);
		//modelViewMatrixStack.translate(0, -min_y, 0);
		Matrix4x4 top;
		modelViewMatrixStack.top(top);
		double rate1 = (double)s / step;
		double rate0 = 1.0 - rate1;
		fout << "控制顶点 " << 2 << " " << cp_num_x * cp_num_y * cp_num_z << endl;
		for (vector<Vector4>::size_type c = 0; c != ctrl_points2.size(); ++c)
		{
			Vector4 p = ctrl_points2[c] * rate0 + ctrl_points1[c] * rate1;
			double result[3] = {0.0};
			for (int i = 0; i < 3; ++i)
				for (int j = 0; j < 4; ++j)
					result[i] += top[j][i] * p[j];
			double k = t * (double)s / (step - 1);
			//fout << "\t" << p[0] << " " << p[1] + v0 * k - 0.5 * g * k * k << " " << p[2] << endl;
			//fout << "\t" << result[0] << " " << result[1] + v0 * k - 0.5 * g * k * k << " " << result[2] << endl;
			fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
		}

		// cubemap旋转矩阵
		fout << "cubemap" << endl << "\t";
		cubeMapMatrixStack.loadIdentity();
		cubeMapMatrixStack.rotate(cubemap_rot_degree * 0.5, 0, 1, 0);
		cubeMapMatrixStack.top(top);
		for (int i = 0; i < 4; ++i)
			for (int j = 0; j < 4; ++j)
				fout << top[i][j] << " ";
		fout << endl;
	}

	// 静止到迈右脚
	for (int s = 0; s < step; ++s)
	{
		modelViewMatrixStack.loadIdentity();
		//modelViewMatrixStack.translate(0, min_y, 0);
		//modelViewMatrixStack.rotate(-180 * s / step, 0, 1, 0);
		//modelViewMatrixStack.translate(0, -min_y, 0);
		Matrix4x4 top;
		modelViewMatrixStack.top(top);
		double rate1 = (double)s / step;
		double rate0 = 1.0 - rate1;
		fout << "控制顶点 " << 2 << " " << cp_num_x * cp_num_y * cp_num_z << endl;
		for (vector<Vector4>::size_type c = 0; c != ctrl_points2.size(); ++c)
		{
			Vector4 p = ctrl_points1[c] * rate0 + ctrl_points3[c] * rate1;
			double result[3] = {0.0};
			for (int i = 0; i < 3; ++i)
				for (int j = 0; j < 4; ++j)
					result[i] += top[j][i] * p[j];
			double k = t * (double)s / (step - 1);
			//fout << "\t" << p[0] << " " << p[1] + v0 * k - 0.5 * g * k * k << " " << p[2] << endl;
			//fout << "\t" << result[0] << " " << result[1] + v0 * k - 0.5 * g * k * k << " " << result[2] << endl;
			fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
		}

		// cubemap旋转矩阵
		fout << "cubemap" << endl << "\t";
		cubeMapMatrixStack.loadIdentity();
		cubeMapMatrixStack.rotate(cubemap_rot_degree, 0, 1, 0);
		cubeMapMatrixStack.top(top);
		for (int i = 0; i < 4; ++i)
			for (int j = 0; j < 4; ++j)
				fout << top[i][j] << " ";
		fout << endl;
	}

	// 迈右脚到静止
	for (int s = 0; s < step; ++s)
	{
		modelViewMatrixStack.loadIdentity();
		//modelViewMatrixStack.translate(0, min_y, 0);
		//modelViewMatrixStack.rotate(-180 * s / step, 0, 1, 0);
		//modelViewMatrixStack.translate(0, -min_y, 0);
		Matrix4x4 top;
		modelViewMatrixStack.top(top);
		double rate1 = (double)s / step;
		double rate0 = 1.0 - rate1;
		fout << "控制顶点 " << 2 << " " << cp_num_x * cp_num_y * cp_num_z << endl;
		for (vector<Vector4>::size_type c = 0; c != ctrl_points2.size(); ++c)
		{
			Vector4 p = ctrl_points3[c] * rate0 + ctrl_points1[c] * rate1;
			double result[3] = {0.0};
			for (int i = 0; i < 3; ++i)
				for (int j = 0; j < 4; ++j)
					result[i] += top[j][i] * p[j];
			double k = t * (double)s / (step - 1);
			//fout << "\t" << p[0] << " " << p[1] + v0 * k - 0.5 * g * k * k << " " << p[2] << endl;
			//fout << "\t" << result[0] << " " << result[1] + v0 * k - 0.5 * g * k * k << " " << result[2] << endl;
			fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
		}

		// cubemap旋转矩阵
		fout << "cubemap" << endl;
		cubeMapMatrixStack.loadIdentity();
		cubeMapMatrixStack.rotate(cubemap_rot_degree * 0.5, 0, 1, 0);
		cubeMapMatrixStack.top(top);
		for (int i = 0; i < 4; ++i)
			for (int j = 0; j < 4; ++j)
				fout << top[i][j] << " ";
		fout << endl;
	}

	//// 偏移到另一侧
	//for (int s = 0; s < step; ++s)
	//{
		//modelViewMatrixStack.loadIdentity();
		//modelViewMatrixStack.translate(0, min_y, 0);
		//modelViewMatrixStack.rotate(-angle * s / step, 1, 0, 0);
		//modelViewMatrixStack.translate(0, -min_y, 0);
		//Matrix4x4 top;
		//modelViewMatrixStack.top(top);
		//double rate1 = (double)s / step;
		//double rate0 = 1.0 - rate1;
		//fout << "控制顶点 " << 2 << " " << 200 << endl;
		//for (vector<Vector4>::size_type c = 0; c != ctrl_points0.size(); ++c)
		//{
			//Vector4 p = ctrl_points0[c] * rate0 + ctrl_points1[c] * rate1;
			//double result[3] = {0.0};
			//for (int i = 0; i < 3; ++i)
				//for (int j = 0; j < 4; ++j)
					//result[i] += top[j][i] * p[j];
			//fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
		//}

		//// cubemap旋转矩阵
		//fout << "cubemap" << endl;
		//cubeMapMatrixStack.loadIdentity();
		//cubeMapMatrixStack.rotate(cubemap_rot_degree * s, 0, 1, 0);
		//cubeMapMatrixStack.top(top);
		//for (int i = 0; i < 4; ++i)
			//for (int j = 0; j < 4; ++j)
				//fout << top[i][j] << " ";
		//fout << endl;
	//}

	//// 第二次回来
	//for (int s = step - 1; s >= 0; --s)
	//{
		//modelViewMatrixStack.loadIdentity();
		//modelViewMatrixStack.translate(0, min_y, 0);
		//modelViewMatrixStack.rotate(-angle * s / step, 1, 0, 0);
		//modelViewMatrixStack.translate(0, -min_y, 0);
		//Matrix4x4 top;
		//modelViewMatrixStack.top(top);
		//double rate1 = (double)s / step;
		//double rate0 = 1.0 - rate1;
		//fout << "控制顶点 " << 2 << " " << 200 << endl;
		//for (vector<Vector4>::size_type c = 0; c != ctrl_points0.size(); ++c)
		//{
			//Vector4 p = ctrl_points0[c] * rate0 + ctrl_points1[c] * rate1;
			//double result[3] = {0.0};
			//for (int i = 0; i < 3; ++i)
				//for (int j = 0; j < 4; ++j)
					//result[i] += top[j][i] * p[j];
			//fout << "\t" << result[0] << " " << result[1] << " " << result[2] << endl;
		//}

		//// cubemap旋转矩阵
		//fout << "cubemap" << endl;
		//cubeMapMatrixStack.loadIdentity();
		//cubeMapMatrixStack.rotate(cubemap_rot_degree * s, 0, 1, 0);
		//cubeMapMatrixStack.top(top);
		//for (int i = 0; i < 4; ++i)
			//for (int j = 0; j < 4; ++j)
				//fout << top[i][j] << " ";
		//fout << endl;
	//}

	fout.close();
	fout.clear();

	return 0;
}
