#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;

int main()
{
	ifstream fin;
	ofstream fout("/home/cym/program/OBJ/algorithm2/bluebird/output.target");

	int iterNum = 3;
	for (int iter = 0; iter < iterNum; ++iter)
	{
		for (int i = 0; i < 8; ++i)
		{
			if (iter != 0 && i == 0)
				continue;
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
						double m = 2;
						double left = -m + iter * m * 2 / iterNum;
						double right = -m + (iter + 1) * m * 2 / iterNum;
						z += (right - left) / 7 * i + left;
						fout << x << ' ' << y << ' ' << z << endl;
					}
				}
			}
			fin.close();
		}
	}

	fout.close();

	return 0;
}
