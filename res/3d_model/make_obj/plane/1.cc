#include <cstdio>

const int N = 30;
const int M = 20;

int top[N + 1][M + 1];
int bottom[N + 1][M + 1];

void writeface(int a, int b, int c, int d, FILE *file)
{
	fprintf(file, "f %d %d %d\n", a, b, c);	
	fprintf(file, "f %d %d %d\n", a, c, d);
}

int main()
{
	int i, j, k;
		
	FILE *file = fopen("plane.obj", "w");

	float move = 12.0f;
	k=1;
	// bottom
	for (i = 0; i < N; i ++)
	{
		for (j = 0; j < M; j++)
		{
			//fprintf(file, "v %.5f  %.5f  %.5f\n", float(i), float(j), 0.0f);
			float x = float(i);
			float y = float(j);
			if (i == 0)
				x -= move;
			if (i == N - 1)
				x += move;
			if (j == 0)
				y -= move;
			if (j == M - 1)
				y += move;
			fprintf(file, "v %.5f  %.5f  %.5f\n", x, y, 0.0f);
			bottom[i][j] = k++;
		}
	}

	// top
	for (i = 0; i < N; i ++)
	{
		for (j = 0; j < M; j++)
		{
			//fprintf(file, "v %.5f  %.5f  %.5f\n", float(i), float(j), 1.0f);
			float x = float(i);
			float y = float(j);
			if (i == 0)
				x -= move;
			if (i == N - 1)
				x += move;
			if (j == 0)
				y -= move;
			if (j == M - 1)
				y += move;
			fprintf(file, "v %.5f  %.5f  %.5f\n", x, y, 1.0f);
			top[i][j] = k++;
		}
	}

	// อุฦห Inside
	for (i = 0; i +1 < N; i++)
	{
		for (j = 0; j +1 < M; j++)
		{
			fprintf(file, "f %d %d %d\n", top[i][j], top[i+1][j], top[i+1][j+1]);
			fprintf(file, "f %d %d %d\n", top[i][j], top[i+1][j+1], top[i][j+1]);

			fprintf(file, "f %d %d %d\n", bottom[i][j], bottom[i+1][j+1], bottom[i+1][j]);
			fprintf(file, "f %d %d %d\n", bottom[i][j], bottom[i][j+1], bottom[i+1][j+1]);
		}
	}

	// อุฦห Boundary
	i=0;
	for (j = 0; j + 1 < M; j++)
	{
		writeface(top[i][j], top[i][j+1], bottom[i][j+1], bottom[i][j],file);
	}

	i=N-1;
	for (j = 0; j + 1 < M; j++)
	{
		writeface(top[i][j], bottom[i][j], bottom[i][j+1], top[i][j+1],file);
	}

	j=0;
	for (i = 0; i + 1 < N; i++)
	{
		writeface(top[i][j], bottom[i][j], bottom[i+1][j], top[i+1][j],file);
	}

	j=M-1;
	for (i = 0; i + 1 < N; i++)
	{
		writeface(top[i][j], top[i+1][j], bottom[i+1][j], bottom[i][j],file);
	}

	fclose(file);

	return 0;
}
