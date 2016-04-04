#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>

using namespace std;

const double PI = 3.14159265358979;

int main()
{
	ifstream fin;
	ofstream fout("/home/cym/program/OBJ/algorithm2/bluebird/output.target");

	double translateX = -1.5;
	int iterNum = 6;
	int fileNum = 8;
	for (int iter = 0; iter < iterNum; ++iter)
	{
		for (int i = 0; i < fileNum; ++i)
		{
			//if (iter != 0 && i == 0)
				//continue;
			ostringstream oss;
			oss << i << ".edit";
			string fileName(oss.str());
			fileName = string("/home/cym/program/OBJ/algorithm2/bluebird/") + fileName;
			fin.open(fileName.c_str());

			string line;
			while(getline(fin, line))
			{
				istringstream iss(line);
				string name;
				iss >> name;
				if (name == "控制顶点")
				{
					int ctrlPointNum;
					iss >> ctrlPointNum;
					fout << name  << ' ' << 20 << ' ' << ctrlPointNum << endl;
					for (int j = 0; j < ctrlPointNum; ++j)
					{
						getline(fin, line);
						double x, y, z;
						istringstream pointStream(line);
						pointStream >> x >> y >> z;
						x += translateX;
						double x1 = x, y1 = y, z1 = z;
						double rad = PI * 2 * (iter + (double)i / fileNum) / iterNum;
						x1 = z * sin(rad) + x * cos(rad);
						y1 = y;
						z1 = z * cos(rad) - x * sin(rad);
						fout << x1 << ' ' << y1 << ' ' << z1 << endl;
					}
				}
			}
			fin.close();
		}
	}

	fout.close();

	return 0;
}
