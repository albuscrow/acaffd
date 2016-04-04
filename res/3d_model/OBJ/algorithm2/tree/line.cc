#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;

int main()
{
	ifstream fin;
	ofstream fout("/home/cym/program/OBJ/algorithm2/tree/output.target");

	int iterNum = 1;
	int time = 3;
	//				 	0,	1,	2,	3,	4,	5,	6,	7,	8,	9,	10, 11, 12
	int fileList[] = {	0,	1,	2,	3,	4,	5,	6,	7,	8,	9,	10,

						9,	8,	7,	10,	8,	9,	10,	10,	8,	7,	9,
						7,	10,	8,	9,	6,	7,	10,	8,
						9,	10,	8,	10,	9,	10,	9,	8,

						9,	8,	7,	6,	5,	4,	3,	2,	1,	0,

						//1,	2,	1,	0,	11,	12,	13,	12,	11,	0,
						//1,	0,	11,	12,	11,	0,
						//1,	0,	11,	0,

						101,102,103,102,101,0,	99,	98,	97,	98, 99,
						0,	101,102,101,0,
						99,	98,	99,	0,
						101,0,	99,	0,

						0,	0,	0,	0,
	};
	//				 	0,	1,	2,	3,	4,	5,	6,	7,	8,	9,	10, 11, 12
	int timeList[] = {	3,	3,	3,	3,	3,	3,	3,	3,	3,	3,	3,

						3,	3,	3,	3,	3,	3,	3,	3,	3,	3,	3,
						3,	3,	3,	3,	3,	3,	3,	3,
						3,	3,	3,	3,	3,	3,	3,	3,

						3,	3,	3,	3,	3,	3,	3,	3,	3,	3,

						4,	4,	4,	4,	4,	4,	5,	5,	5,	5, 5,
						6,	6,	6,	6,	6,
						7,	7,	7,	7,
						8,	8,	8,	8,

						20,	20,	20,	20,
	};
	int fileNum = sizeof(fileList) / sizeof(int);
	cout << "fileNum = " << fileNum << endl;
	cout << "timeNum = " << sizeof(timeList) / sizeof(int) << endl;
	for (int iter = 0; iter < iterNum; ++iter)
	{
		for (int i = 0; i < fileNum; ++i)
		{
			if (iter != 0 && i == 0)
				continue;
			ostringstream oss;
			oss << fileList[i] << ".edit";
			string fileName(oss.str());
			fileName = string("/home/cym/program/OBJ/algorithm2/tree/") + fileName;
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
					//fout << name  << ' ' << time << ' ' << ctrlPointNum << endl;
					fout << name  << ' ' << timeList[i] << ' ' << ctrlPointNum << endl;
					for (int j = 0; j < ctrlPointNum; ++j)
					{
						getline(fin, line);
						double x, y, z;
						istringstream pointStream(line);
						pointStream >> x >> y >> z;
						//double m = 2;
						//double left = -m + iter * m * 2 / iterNum;
						//double right = -m + (iter + 1) * m * 2 / iterNum;
						//z += (right - left) / fileNum * i + left;
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
