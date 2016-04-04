#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>

using namespace std;

const double PI = 3.14159265358979;
const double ZERO = 0.000001;

int main()
{
	ifstream fin;
	ofstream fout("output.target");

	double translateZ = 1.5;
	int iterNum = 20;
	int fileNum = 4;
	int stepNum = iterNum * fileNum;
	double a = 1;
	for (int iter = 0; iter < iterNum; ++iter)
	{
		for (int i = 0; i < fileNum; ++i)
		{
			
			double t = PI * 2 * (iter + (double)i / fileNum) / iterNum;
			double xx = a * sqrt(2.0) * cos(t) / (1 + sin(t) * sin(t));
			double yy = xx * sin(t);
			double theta;
			if (fabs(yy) <= ZERO && fabs(xx) > ZERO)
			{
				if (xx > 0)				// 最右端
				{
					theta = -PI / 2;
					cout << "teshu > 0" << endl;
				}
				else					// 最左端
				{
					theta = -PI / 2;
					cout << "teshu < 0" << endl;
				}
			}
			else if (fabs(yy) <= ZERO && fabs(xx) <= ZERO)
			{
				if (iter < iterNum / 2)
				{
					theta = PI / 4;
					cout << "teshu2 > 0" << endl;
				}
				else
				{
					theta = -PI / 4;
					cout << "teshu2 < 0" << endl;
				}
			}
			else
			{
				double tanTheta = xx * (a * a - xx * xx - yy * yy) /
								  (yy * (a * a + xx * xx + yy * yy));
				theta = atan(tanTheta);
			}
			int step = iter * fileNum + i;
			if (step <= stepNum / 2)
			{
				theta += PI;
			}

			ostringstream oss;
			oss << i << ".edit";
			string fileName(oss.str());
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
					fout << name  << ' ' << 40 << ' ' << ctrlPointNum << endl;
					for (int j = 0; j < ctrlPointNum; ++j)
					{
						getline(fin, line);
						double x, y, z;
						istringstream pointStream(line);
						pointStream >> x >> y >> z;
						double x1 = z * sin(theta) + x * cos(theta);
						double y1 = y;
						double z1 = z * cos(theta) - x * sin(theta);
						x1 += xx;
						z1 -= yy;
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
