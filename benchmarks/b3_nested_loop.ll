; ModuleID = 'D:\Sem 5 Projects\PGARA\benchmarks\b3_nested_loop.c'
source_filename = "D:\\Sem 5 Projects\\PGARA\\benchmarks\\b3_nested_loop.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @matrix_multiply(i32 noundef %0, ptr noundef %1, ptr noundef %2, ptr noundef %3) #0 {
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca ptr, align 8
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  %11 = alloca i32, align 4
  %12 = alloca i32, align 4
  store ptr %3, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store ptr %1, ptr %7, align 8
  store i32 %0, ptr %8, align 4
  store i32 0, ptr %9, align 4
  br label %13

13:                                               ; preds = %66, %4
  %14 = load i32, ptr %9, align 4
  %15 = load i32, ptr %8, align 4
  %16 = icmp slt i32 %14, %15
  br i1 %16, label %17, label %69

17:                                               ; preds = %13
  store i32 0, ptr %10, align 4
  br label %18

18:                                               ; preds = %62, %17
  %19 = load i32, ptr %10, align 4
  %20 = load i32, ptr %8, align 4
  %21 = icmp slt i32 %19, %20
  br i1 %21, label %22, label %65

22:                                               ; preds = %18
  store i32 0, ptr %11, align 4
  store i32 0, ptr %12, align 4
  br label %23

23:                                               ; preds = %49, %22
  %24 = load i32, ptr %12, align 4
  %25 = load i32, ptr %8, align 4
  %26 = icmp slt i32 %24, %25
  br i1 %26, label %27, label %52

27:                                               ; preds = %23
  %28 = load ptr, ptr %7, align 8
  %29 = load i32, ptr %9, align 4
  %30 = load i32, ptr %8, align 4
  %31 = mul i32 %29, %30
  %32 = load i32, ptr %12, align 4
  %33 = add i32 %31, %32
  %34 = sext i32 %33 to i64
  %35 = getelementptr inbounds i32, ptr %28, i64 %34
  %36 = load i32, ptr %35, align 4
  %37 = load ptr, ptr %6, align 8
  %38 = load i32, ptr %12, align 4
  %39 = load i32, ptr %8, align 4
  %40 = mul i32 %38, %39
  %41 = load i32, ptr %10, align 4
  %42 = add i32 %40, %41
  %43 = sext i32 %42 to i64
  %44 = getelementptr inbounds i32, ptr %37, i64 %43
  %45 = load i32, ptr %44, align 4
  %46 = mul i32 %36, %45
  %47 = load i32, ptr %11, align 4
  %48 = add i32 %47, %46
  store i32 %48, ptr %11, align 4
  br label %49

49:                                               ; preds = %27
  %50 = load i32, ptr %12, align 4
  %51 = add i32 %50, 1
  store i32 %51, ptr %12, align 4
  br label %23, !llvm.loop !7

52:                                               ; preds = %23
  %53 = load i32, ptr %11, align 4
  %54 = load ptr, ptr %5, align 8
  %55 = load i32, ptr %9, align 4
  %56 = load i32, ptr %8, align 4
  %57 = mul i32 %55, %56
  %58 = load i32, ptr %10, align 4
  %59 = add i32 %57, %58
  %60 = sext i32 %59 to i64
  %61 = getelementptr inbounds i32, ptr %54, i64 %60
  store i32 %53, ptr %61, align 4
  br label %62

62:                                               ; preds = %52
  %63 = load i32, ptr %10, align 4
  %64 = add i32 %63, 1
  store i32 %64, ptr %10, align 4
  br label %18, !llvm.loop !9

65:                                               ; preds = %18
  br label %66

66:                                               ; preds = %65
  %67 = load i32, ptr %9, align 4
  %68 = add i32 %67, 1
  store i32 %68, ptr %9, align 4
  br label %13, !llvm.loop !10

69:                                               ; preds = %13
  ret void
}

attributes #0 = { noinline nounwind optnone uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5}
!llvm.ident = !{!6}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)", isOptimized: false, runtimeVersion: 0, emissionKind: NoDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "D:\\Sem 5 Projects\\PGARA\\benchmarks\\b3_nested_loop.c", directory: "D:\\Sem 5 Projects\\PGARA")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 8, !"PIC Level", i32 2}
!4 = !{i32 7, !"uwtable", i32 2}
!5 = !{i32 1, !"MaxTLSAlign", i32 65536}
!6 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
!7 = distinct !{!7, !8}
!8 = !{!"llvm.loop.mustprogress"}
!9 = distinct !{!9, !8}
!10 = distinct !{!10, !8}
