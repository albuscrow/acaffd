#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <cmath>

using namespace std;

const double PI = 3.14159265358979;

int main()
{
	ifstream fin("input.bak");
	ofstream fout("/home/cym/program/animation/input");

	int xCount, yCount, zCount;
	fin >> xCount >> yCount >> zCount;
	fout << xCount << ' ' << yCount << ' ' << zCount << endl;
	for (int i = 0; i <= xCount * yCount * zCount; ++i)
	{
		string line;
		getline(fin, line);
		if (i > 0)
			fout << line << endl;
	}

	double signalX[] = {1.0, -1.0, -1.0, 1.0, 1.0};
	double signalY[] = {-1.0, -1.0, 1.0, 1.0, -1.0};
	double translationTime = 30;
	double startPoint = 2.5;
	double speed = (startPoint + 1) / translationTime;
	for (int corner = 0; corner < 4; ++corner)
	{
		// 定位到起点角落，0:右下 1:左下 2:左上 3:右上
		fout << endl;
		fout << "#\t时间\t基准\t操作数" << endl;
		fout << "状态\t" << translationTime << "\t0\t3" << endl;
		fout << "#\t\t操作\t轴\t量\t切片方向\t切片数量\t切片编号" << endl;
		fout << "旋转\tz\t" << -corner * 90 << "\ty\t5\t0 1 2 3 4" << endl;
		if (corner % 2 == 0)
		{
			fout << "平移\tx\t" << 1.0 * signalX[corner] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << "平移\ty\t" << 4.0 * signalY[corner]<< "\ty\t5\t0 1 2 3 4" << endl;
		}
		else
		{
			fout << "平移\tx\t" << 4.0 * signalX[corner] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << "平移\ty\t" << 1.0 * signalY[corner]<< "\ty\t5\t0 1 2 3 4" << endl;
		}

		// 压缩
		fout << endl;
		fout << "#\t时间\t基准\t操作数" << endl;
		fout << "状态\t30\t0\t6" << endl;
		fout << "#\t\t操作\t轴\t量\t切片方向\t切片数量\t切片编号" << endl;
		fout << "旋转\tz\t" << -corner * 90 << "\ty\t5\t0 1 2 3 4" << endl;
		if (corner % 2 == 0)
		{
			fout << "缩放\tx\t0.5\ty\t5\t0 1 2 3 4" << endl;
			fout << "缩放\ty\t2.0\ty\t5\t0 1 2 3 4" << endl;
			fout << "缩放\tz\t2.0\ty\t5\t0 1 2 3 4" << endl;
		}
		else
		{
			fout << "缩放\tx\t2.0\ty\t5\t0 1 2 3 4" << endl;
			fout << "缩放\ty\t0.5\ty\t5\t0 1 2 3 4" << endl;
			fout << "缩放\tz\t2.0\ty\t5\t0 1 2 3 4" << endl;
		}

		if (corner % 2 == 0)
		{
			fout << "平移\tx\t" << startPoint * signalX[corner] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << "平移\ty\t" << 4.0 * signalY[corner]<< "\ty\t5\t0 1 2 3 4" << endl;
		}
		else
		{
			fout << "平移\tx\t" << 4.0 * signalX[corner] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << "平移\ty\t" << startPoint * signalY[corner]<< "\ty\t5\t0 1 2 3 4" << endl;
		}

		// 定位到终点角落，0:左下 1:左上 2:右上 3:右下
		fout << endl;
		fout << "#\t时间\t基准\t操作数" << endl;
		fout << "状态\t2\t0\t3" << endl;
		fout << "#\t\t操作\t轴\t量\t切片方向\t切片数量\t切片编号" << endl;
		fout << "旋转\tz\t" << -corner * 90 << "\ty\t5\t0 1 2 3 4" << endl;
		if (corner % 2 == 0)
		{
			fout << "平移\tx\t" << 1.0 * signalX[corner + 1] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << "平移\ty\t" << 4.0 * signalY[corner + 1]<< "\ty\t5\t0 1 2 3 4" << endl;
		}
		else
		{
			fout << "平移\tx\t" << 4.0 * signalX[corner + 1] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << "平移\ty\t" << 1.0 * signalY[corner + 1]<< "\ty\t5\t0 1 2 3 4" << endl;
		}

		// 10个旋转关键帧
		double a[11] = {-1.0, -0.8888888888, -0.6666666666, -0.4444444444, -0.2222222222, 0,
						0.2222222222, 0.4444444444, 0.6666666666, 0.8888888888, 1.0};
		if (corner == 1 || corner == 2)
		{
			for (int i = 0; i < 11; ++i)
				a[i] *= -1;
		}
		fout.precision(12);
		for (int i = 1; i < 11; ++i)
		{
			int frameNum = i * 3 + 5;
			// 将前i个切片移动到合适位置进行旋转
			fout << endl;
			fout << "#\t时间\t基准\t操作数" << endl;
			//fout << "状态\t" << fabs(a[i] - a[i - 1]) / speed << "\t0\t" << frameNum << endl;
			fout << "状态\t3\t0\t" << frameNum << endl;
			fout << "#\t\t操作\t轴\t量\t切片方向\t切片数量\t切片编号" << endl;
			fout << "旋转\tz\t" << -corner * 90 << "\ty\t5\t0 1 2 3 4" << endl;
			for (int j = 0; j < i; ++j)
			{
				double deltaX, deltaY;
				switch(corner)
				{
					case 0:
						deltaX = -a[j];
						deltaY = -2;
						break;
					case 1:
						deltaX = -2;
						deltaY = -a[j];
						break;
					case 2:
						deltaX = -a[j];
						deltaY = 2;
						break;
					case 3:
						deltaX = 2;
						deltaY = -a[j];
						break;
				}
				fout << "平移\tx\t" << deltaX << "\tx\t1\t" << j << endl;
				fout << "平移\ty\t" << deltaY << "\t\tx\t1\t" << j << endl;
				fout << "旋转\tz\t" << -fabs(a[j] - a[i]) * 90 / PI << "\tx\t1\t" << j << endl;
			}

			// 将前面旋转过的切片移到最终目标
			fout << "平移\tx\t"<< 2.0 * signalX[corner + 1] <<"\tx\t" << i << "\t";
			for (int j = 0; j < i; ++j)
				fout << j << ' ';
			fout << endl;
			fout << "平移\ty\t"<< 2.0 * signalY[corner + 1] <<"\tx\t" << i << "\t";
			for (int j = 0; j < i; ++j)
				fout << j << ' ';
			fout << endl;

			// 将其余的切片移到最终目标
			double deltaX, deltaY;
			switch(corner)
			{
				case 0:
					deltaX = -2 - a[i];
					deltaY = -4.0;
					break;
				case 1:
					deltaX = -4.0;
					deltaY = 2 - a[i];
					break;
				case 2:
					deltaX = 2 - a[i];
					deltaY = 4.0;
					break;
				case 3:
					deltaX = 4.0;
					deltaY = -2 - a[i];
					break;
			}
			fout << "平移\tx\t" << deltaX << "\tx\t" << 11 - i << "\t";
			for (int j = i; j < 11; ++j)
				fout << j << ' ';
			fout << endl;
			fout << "平移\ty\t" << deltaY << "\tx\t" << 11 - i << "\t";
			for (int j = i; j < 11; ++j)
				fout << j << ' ';
			fout << endl;
		}
		fout << endl;

		fout << "继续旋转" << endl;

		int rotationStep = 10;
		// 继续旋转直到最前面的一个切片旋转够90度
		fout << "#\t时间\t时间\t基准\t步数\t操作数" << endl;
		double rotationStepTime = (PI / 2 - 1) / (speed * rotationStep);
		//fout << "序列\t" << rotationStepTime << "\t" << rotationStepTime
			 //<< "\t-1\t"<< rotationStep << "\t6" << endl;
		fout << "序列\t" << 3 << "\t" << 3 << "\t-1\t"<< rotationStep << "\t5" << endl;
		fout << "#\t\t操作\t轴\t量\t切片方向\t切片数量\t切片编号" << endl;
		int prev = corner - 1;
		if (prev < 0)
			prev += 4;
		fout << "平移\tx\t" << 2 * signalX[prev] << "\ty\t5\t0 1 2 3 4" << endl;
		fout << "平移\ty\t" << 2 * signalY[prev] << "\ty\t5\t0 1 2 3 4" << endl;
		fout << "旋转*\tz\t-32.70422049\ty\t5\t0 1 2 3 4" << endl;
		fout << "平移\tx\t" << -2 * signalX[prev] << "\ty\t5\t0 1 2 3 4" << endl;
		fout << "平移\ty\t" << -2 * signalY[prev] << "\ty\t5\t0 1 2 3 4" << endl;

		fout << endl << "从旋转到伸直" << endl;

		// 从旋转伸直的10个关键帧
		for (int i = 1; i < 11; ++i)
		{
			double delta = a[i - 1] - a[i];
			int frameNum = 5 + i;
			// 将圆弧移动到(0, 0)为中心，2为半径的圆上
			fout << "#\t时间\t基准\t操作数" << endl;
			fout << "状态\t3\t-1\t" << frameNum << endl;
			fout << "#\t\t操作\t轴\t量\t切片方向\t切片数量\t切片编号" << endl;
			fout << "平移\tx\t" << 2 * -signalX[corner + 1] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << "平移\ty\t" << 2 * -signalY[corner + 1] << "\ty\t5\t0 1 2 3 4" << endl;
			// 将前i个点直接平移（它们已经走出了圆弧）
			for (int j = 0; j < i; ++j)
			{
				switch(corner)
				{
					case 0:
					case 2:
						fout << "平移\ty\t" << -delta << "\tx\t1\t" << j << endl;
						break;
					case 1:
					case 3:
						fout << "平移\tx\t" << delta << "\tx\t1\t" << j << endl;
						break;
				}
			}
			// 将其余点（尚在圆弧上）旋转
			fout << "旋转\tz\t" << -fabs(delta) * 90 / PI << "\tx\t" << 11 - i << "\t";
			for (int j = i; j < 11; ++j)
				fout << j << ' ';
			fout << endl;
			// 将所有点移回原来的位置
			fout << "平移\tx\t" << 2 * signalX[corner + 1] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << "平移\ty\t" << 2 * signalY[corner + 1] << "\ty\t5\t0 1 2 3 4" << endl;
			fout << endl;
		}
		fout << endl;
	}

	fin.close();
	fout.close();

	return 0;
}
