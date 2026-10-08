; ModuleID = 'results/raw/phase1/b3_nested_loop.raw.ll'
source_filename = "benchmarks\\b3_nested_loop.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

; Function Attrs: noinline nounwind uwtable
define dso_local void @matrix_multiply(i32 noundef %0, ptr noundef %1, ptr noundef %2, ptr noundef %3) #0 {
  br label %5

5:                                                ; preds = %36, %4
  %.03 = phi i32 [ 0, %4 ], [ %37, %36 ]
  %6 = icmp slt i32 %.03, %0
  br i1 %6, label %7, label %38

7:                                                ; preds = %5
  br label %8

8:                                                ; preds = %33, %7
  %.02 = phi i32 [ 0, %7 ], [ %34, %33 ]
  %9 = icmp slt i32 %.02, %0
  br i1 %9, label %10, label %35

10:                                               ; preds = %8
  br label %11

11:                                               ; preds = %26, %10
  %.01 = phi i32 [ 0, %10 ], [ %25, %26 ]
  %.0 = phi i32 [ 0, %10 ], [ %27, %26 ]
  %12 = icmp slt i32 %.0, %0
  br i1 %12, label %13, label %28

13:                                               ; preds = %11
  %14 = mul i32 %.03, %0
  %15 = add i32 %14, %.0
  %16 = sext i32 %15 to i64
  %17 = getelementptr inbounds i32, ptr %1, i64 %16
  %18 = load i32, ptr %17, align 4
  %19 = mul i32 %.0, %0
  %20 = add i32 %19, %.02
  %21 = sext i32 %20 to i64
  %22 = getelementptr inbounds i32, ptr %2, i64 %21
  %23 = load i32, ptr %22, align 4
  %24 = mul i32 %18, %23
  %25 = add i32 %.01, %24
  br label %26

26:                                               ; preds = %13
  %27 = add i32 %.0, 1
  br label %11, !llvm.loop !7

28:                                               ; preds = %11
  %29 = mul i32 %.03, %0
  %30 = add i32 %29, %.02
  %31 = sext i32 %30 to i64
  %32 = getelementptr inbounds i32, ptr %3, i64 %31
  store i32 %.01, ptr %32, align 4
  br label %33

33:                                               ; preds = %28
  %34 = add i32 %.02, 1
  br label %8, !llvm.loop !9

35:                                               ; preds = %8
  br label %36

36:                                               ; preds = %35
  %37 = add i32 %.03, 1
  br label %5, !llvm.loop !10

38:                                               ; preds = %5
  ret void
}

attributes #0 = { noinline nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5}
!llvm.ident = !{!6}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)", isOptimized: false, runtimeVersion: 0, emissionKind: NoDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "benchmarks\\b3_nested_loop.c", directory: "D:\\Sem 5 Projects\\PGARA")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 8, !"PIC Level", i32 2}
!4 = !{i32 7, !"uwtable", i32 2}
!5 = !{i32 1, !"MaxTLSAlign", i32 65536}
!6 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
!7 = distinct !{!7, !8}
!8 = !{!"llvm.loop.mustprogress"}
!9 = distinct !{!9, !8}
!10 = distinct !{!10, !8}
