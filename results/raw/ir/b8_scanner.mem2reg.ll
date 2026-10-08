; ModuleID = 'results\raw\ir\b8_scanner.raw.ll'
source_filename = "benchmarks\\b8_scanner.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @count_tokens(ptr noundef %0) #0 {
  br label %2

2:                                                ; preds = %27, %1
  %.02 = phi i32 [ 0, %1 ], [ %.13, %27 ]
  %.01 = phi i32 [ 0, %1 ], [ %.1, %27 ]
  %.0 = phi i32 [ 0, %1 ], [ %28, %27 ]
  %3 = sext i32 %.0 to i64
  %4 = getelementptr inbounds i8, ptr %0, i64 %3
  %5 = load i8, ptr %4, align 1
  %6 = sext i8 %5 to i32
  %7 = icmp ne i32 %6, 0
  br i1 %7, label %8, label %29

8:                                                ; preds = %2
  %9 = sext i32 %.0 to i64
  %10 = getelementptr inbounds i8, ptr %0, i64 %9
  %11 = load i8, ptr %10, align 1
  %12 = sext i8 %11 to i32
  %13 = icmp eq i32 %12, 32
  br i1 %13, label %20, label %14

14:                                               ; preds = %8
  %15 = sext i8 %11 to i32
  %16 = icmp eq i32 %15, 9
  br i1 %16, label %20, label %17

17:                                               ; preds = %14
  %18 = sext i8 %11 to i32
  %19 = icmp eq i32 %18, 10
  br i1 %19, label %20, label %21

20:                                               ; preds = %17, %14, %8
  br label %26

21:                                               ; preds = %17
  %22 = icmp ne i32 %.02, 0
  br i1 %22, label %25, label %23

23:                                               ; preds = %21
  %24 = add i32 %.01, 1
  br label %25

25:                                               ; preds = %23, %21
  %.24 = phi i32 [ %.02, %21 ], [ 1, %23 ]
  %.2 = phi i32 [ %.01, %21 ], [ %24, %23 ]
  br label %26

26:                                               ; preds = %25, %20
  %.13 = phi i32 [ 0, %20 ], [ %.24, %25 ]
  %.1 = phi i32 [ %.01, %20 ], [ %.2, %25 ]
  br label %27

27:                                               ; preds = %26
  %28 = add i32 %.0, 1
  br label %2, !llvm.loop !7

29:                                               ; preds = %2
  ret i32 %.01
}

attributes #0 = { noinline nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5}
!llvm.ident = !{!6}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)", isOptimized: false, runtimeVersion: 0, emissionKind: NoDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "benchmarks\\b8_scanner.c", directory: "D:\\Sem 5 Projects\\PGARA")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 8, !"PIC Level", i32 2}
!4 = !{i32 7, !"uwtable", i32 2}
!5 = !{i32 1, !"MaxTLSAlign", i32 65536}
!6 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
!7 = distinct !{!7, !8}
!8 = !{!"llvm.loop.mustprogress"}
