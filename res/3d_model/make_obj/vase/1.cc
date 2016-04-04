#include "obj_data.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <set>

using namespace std;
using namespace objdata;

ObjData obj_data;

void output()
{
	ofstream fout("vase_cym.obj");
	// 输出顶点
	for (vector<VertexCoord>::size_type i = 0; i < obj_data.vertexCoordList.size(); ++i)
	{
		fout << "v " << obj_data.vertexCoordList[i].x()
			 << " " << obj_data.vertexCoordList[i].y()
			 << " " << obj_data.vertexCoordList[i].z() << endl;
	}
	// 输出纹理坐标
	for (vector<TextureCoord>::size_type i = 0; i < obj_data.textureCoordList.size(); ++i)
	{
		fout << "vt " << obj_data.textureCoordList[i].u()
			 << " " << obj_data.textureCoordList[i].v() << endl;
	}
	// 输出法向
	for (vector<NormalCoord>::size_type i = 0; i < obj_data.normalCoordList.size(); ++i)
	{
		fout << "vn " << obj_data.normalCoordList[i].i()
			 << " " << obj_data.normalCoordList[i].j()
			 << " " << obj_data.normalCoordList[i].k() << endl;
	}
	// 输出面片
	for (vector<Face>::size_type i = 0; i < obj_data.faceList.size(); ++i)
	{
		fout << "f";
		for (int j = 0; j < 3; ++j)
		{
			fout << " " << obj_data.faceList[i].vertexCoordIndex[j] + 1
				 << "/" << obj_data.faceList[i].textureCoordIndex[j] + 1
				 << "/" << obj_data.faceList[i].normalCoordIndex[j] + 1;
		}
		fout << endl;
	}
	fout.close();
	fout.clear();
}

int abnormal_v_id[] = {34, 36, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233};
int abnormal_size = sizeof(abnormal_v_id) / sizeof(int);
vector<set<int> > abnormal_normals;

// 如果face_id含有异常顶点，则将其对应法向存入abnormal_normals;
void getErrorFacesNormal(int face_id)
{
	int v_id[3];
	for (int i = 0; i < 3; ++i)
	{
		v_id[i] = obj_data.faceList[face_id].vertexCoordIndex[i];
		int abnormal_id;
		for (abnormal_id = 0; abnormal_id < abnormal_size; ++abnormal_id)
		{
			if (v_id[i] == abnormal_v_id[abnormal_id])
				break;
		}
		if (abnormal_id < abnormal_size)	// 说明当前顶点确实是异常顶点
		{
			int n_id = obj_data.faceList[face_id].normalCoordIndex[i];
			if (n_id > 2)
				abnormal_normals[abnormal_id].insert(n_id);
		}
	}
}

void modifyAllFace(int source_n_id, int target_n_id)
{
	cout << "size = " << obj_data.faceList.size() << endl;
	for (vector<Face>::size_type i = 0; i < obj_data.faceList.size(); ++i)
	{
		int n_id[3];
		for (int j = 0; j < 3; ++j)
		{
			n_id[j] = obj_data.faceList[i].normalCoordIndex[j];
			if (n_id[j] == source_n_id)
			{
				obj_data.faceList[i].normalCoordIndex[j] = target_n_id;
			}
		}
	}
}

int main()
{
	obj_data.readObj("vase.obj");

	for (int i = 0; i < abnormal_size; ++i)
	{
		set<int> temp;
		abnormal_normals.push_back(temp);
	}
	for (vector<Face>::size_type i = 0; i < obj_data.faceList.size(); ++i)
		getErrorFacesNormal(i);

	for (vector<set<int> >::size_type i = 0; i < abnormal_normals.size(); ++i)
	{
		int normal_count = abnormal_normals[i].size();
		int n_id[4];
		set<int>::iterator it = abnormal_normals[i].begin();
		n_id[0] = *it++;
		n_id[1] = *it++;
		NormalCoord n0 = obj_data.normalCoordList[n_id[0]];
		NormalCoord n1 = obj_data.normalCoordList[n_id[1]];
		if (normal_count > 2)
		{
			n_id[2] = *it++;
			n_id[3] = *it++;
			cout << "0 = " << n_id[0] << ", 1 = " << n_id[1] << ", 2 = " << n_id[2]
				 << ", 3 = " << n_id[3] << endl;
			NormalCoord n2 = obj_data.normalCoordList[n_id[2]];
			NormalCoord n3 = obj_data.normalCoordList[n_id[3]];
			NormalCoord n_ave0 = (n0 + n2) * 0.5;
			n_ave0.normalize();
			NormalCoord n_ave1 = (n1 + n3) * 0.5;
			n_ave1.normalize();
			obj_data.normalCoordList[n_id[2]] = n_ave0;
			obj_data.normalCoordList[n_id[3]] = n_ave1;
			modifyAllFace(n_id[2], n_id[0]);
			modifyAllFace(n_id[3], n_id[1]);
		}
		else
		{
			cout << "0 = " << n_id[0] << ", 1 = " << n_id[1] << endl;
			NormalCoord n_ave = (n0 + n1) * 0.5;
			n_ave.normalize();
			obj_data.normalCoordList[n_id[1]] = n_ave;
			modifyAllFace(n_id[1], n_id[0]);
		}
	}

	for (int i = 0; i < abnormal_size; ++i)
	{
		cout << abnormal_v_id[i] << ": ";
		for (set<int>::iterator it = abnormal_normals[i].begin(); it != abnormal_normals[i].end(); ++it)
			cout << *it << " ";
		cout << endl;
	}

	// 测试用，移动所有的异常顶点
	//for (int i = 0; i < abnormal_size; ++i)
	//{
		//double a = obj_data.vertexCoordList[abnormal_v_id[i]].x();
		//obj_data.vertexCoordList[abnormal_v_id[i]].x(a + 20);
	//}
		//double a = obj_data.vertexCoordList[231].x();
		//obj_data.vertexCoordList[231].x(a + 20);

	output();		// 输出新模型

	return 0;
}
