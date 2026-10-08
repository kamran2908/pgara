; ModuleID = 'results\raw\ir\b5_rare_error.raw.ll'
source_filename = "benchmarks\\b5_rare_error.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

; Function Attrs: noinline nounwind uwtable
define dso_local void @log_error(i32 noundef %0) #0 {
  ret void
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @compute(i32 noundef %0, ptr noundef %1) #0 {
  br label %3

3:                                                ; preds = %18, %2
  %.02 = phi i32 [ 0, %2 ], [ %17, %18 ]
  %.01 = phi i32 [ 0, %2 ], [ %.1, %18 ]
  %.0 = phi i32 [ 0, %2 ], [ %19, %18 ]
  %4 = icmp slt i32 %.0, %0
  br i1 %4, label %5, label %20

5:                                                ; preds = %3
  %6 = sext i32 %.0 to i64
  %7 = getelementptr inbounds i32, ptr %1, i64 %6
  %8 = load i32, ptr %7, align 4
  %9 = icmp slt i32 %8, 0
  br i1 %9, label %10, label %12

10:                                               ; preds = %5
  %11 = add i32 %.01, 1
  call void @log_error(i32 noundef %.0)
  br label %12

12:                                               ; preds = %10, %5
  %.1 = phi i32 [ %11, %10 ], [ %.01, %5 ]
  %13 = sext i32 %.0 to i64
  %14 = getelementptr inbounds i32, ptr %1, i64 %13
  %15 = load i32, ptr %14, align 4
  %16 = mul i32 %15, 2
  %17 = add i32 %.02, %16
  br label %18

18:                                               ; preds = %12
  %19 = add i32 %.0, 1
  br label %3, !llvm.loop !7

20:                                               ; preds = %3
  %21 = add i32 %.02, %.01
  ret i32 %21
}

attributes #0 = { noinline nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5}
!llvm.ident = !{!6}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)", isOptimized: false, runtimeVersion: 0, emissionKind: NoDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "benchmarks\\b5_rare_error.c", directory: "D:\\Sem 5 Projects\\PGARA")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 8, !"PIC Level", i32 2}
!4 = !{i32 7, !"uwtable", i32 2}
!5 = !{i32 1, !"MaxTLSAlign", i32 65536}
!6 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
!7 = distinct !{!7, !8}
!8 = !{!"llvm.loop.mustprogress"}
