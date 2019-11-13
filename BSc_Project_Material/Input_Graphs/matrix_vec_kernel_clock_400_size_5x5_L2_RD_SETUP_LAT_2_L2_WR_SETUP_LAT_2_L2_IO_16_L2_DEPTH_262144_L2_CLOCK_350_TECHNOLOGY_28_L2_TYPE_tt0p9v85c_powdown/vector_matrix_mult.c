#include <stdio.h>


#define DIM1 5
#define DIM2 5

void initialize_matrices(int *A, int *B, int *C, int *D, int *E);
void matrix_vec_kernel(int *A,int *B, int *C);
void matrix_matrix_kernel(int *A,int *D, int *E);
void print_vector(int *C);
void print_matrix(int *A);

int main(){
    int A[DIM1][DIM2];
    int B[DIM2];
    int C[DIM1];
    int D[DIM1][DIM2];
    int E[DIM1][DIM2];

    printf("### matrix_vec kernel: ###\n");
    printf("initialize_matrices\n");
    initialize_matrices((int*)A,B,C,(int*)D,(int*)E);
    printf("Matrix A: \n");
    print_matrix((int *)A);
    printf("Vector B: \n");
    print_vector(B);
    printf("run matrix_vec_kernel\n");
    matrix_vec_kernel((int *)A,B,C);
    printf("print_vector\n");
    print_vector(C);
    
    printf("### matrix_matrix kernel: ###\n");
    printf("initialize_matrices\n");
    printf("Matrix A: \n");
    print_matrix((int *)A);
    printf("Matrix D: \n");
    print_matrix((int *)D);
    printf("run matrix_matrix_kernel\n");
    matrix_matrix_kernel((int *)A,(int *)D,(int *)E);
    printf("Matrix D: \n");
    print_matrix((int *)E);
    
}

void initialize_matrices(int *A, int *B, int *C, int *D, int *E){
    for(int i=0;i<DIM2;i++)
        B[i]=i;
    for(int i=0;i<DIM1;i++){
        C[i]=0;
        for (int j=0;j<DIM2;j++){
            A[i*DIM1+j]=i*DIM1+j;
            D[i*DIM1+j]=i*DIM1+j;
            E[i*DIM1+j]=0;
        }
    }
}

void matrix_vec_kernel(int *A,int *B, int *C){
    int sum;
    #pragma clang loop unroll(full)
    for(int i=0;i<DIM2;i++){
        sum=0;
        #pragma clang loop unroll(full)
        for(int j=0;j<DIM1;j++){
            sum+=A[i*DIM1+j]*B[j];
        }
        C[i]=sum;
    }
}

void matrix_matrix_kernel(int *A,int *D, int *E){
    int sum;
    #pragma clang loop unroll(full)
    for(int i=0;i<DIM2;i++){
        #pragma clang loop unroll(full)
        for(int j=0;j<DIM1;j++){
            sum=0;
            #pragma clang loop unroll(full)
            for(int k=0;k<DIM2;k++){
                sum+=A[i*DIM1+k]*D[k*DIM1+j];
            }
            E[i*DIM1+j] = sum;
        }
    }
}

void print_matrix(int *A){
    for(int i=0;i<DIM2;i++){
        for(int j=0;j<DIM1;j++){
            printf("%d ",A[i*DIM1+j]);
        }
        printf("\n");
    }

}
void print_vector(int *C){
    for(int i=0;i<DIM1;i++){
        printf("[%d] = %d\n",i,C[i]);
    }
}
