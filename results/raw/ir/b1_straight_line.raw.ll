; ModuleID = 'benchmarks\b1_straight_line.c'
source_filename = "benchmarks\\b1_straight_line.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @compute_arithmetic(i32 noundef %0, i32 noundef %1, i32 noundef %2) #0 {
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  store i32 %2, ptr %4, align 4
  store i32 %1, ptr %5, align 4
  store i32 %0, ptr %6, align 4
  %11 = load i32, ptr %6, align 4
  %12 = load i32, ptr %5, align 4
  %13 = add i32 %11, %12
  store i32 %13, ptr %7, align 4
  %14 = load i32, ptr %7, align 4
  %15 = load i32, ptr %4, align 4
  %16 = mul i32 %14, %15
  store i32 %16, ptr %8, align 4
  %17 = load i32, ptr %8, align 4
  %18 = load i32, ptr %6, align 4
  %19 = sub i32 %17, %18
  store i32 %19, ptr %9, align 4
  %20 = load i32, ptr %9, align 4
  %21 = load i32, ptr %5, align 4
  %22 = add i32 %21, 1
  %23 = sdiv i32 %20, %22
  store i32 %23, ptr %10, align 4
  %24 = load i32, ptr %10, align 4
  %25 = load i32, ptr %7, align 4
  %26 = add i32 %24, %25
  %27 = load i32, ptr %8, align 4
  %28 = add i32 %26, %27
  %29 = load i32, ptr %9, align 4
  %30 = add i32 %28, %29
  ret i32 %30
}

attributes #0 = { noinline nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5}
!llvm.ident = !{!6}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)", isOptimized: false, runtimeVersion: 0, emissionKind: NoDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "benchmarks\\b1_straight_line.c", directory: "D:\\Sem 5 Projects\\PGARA")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 8, !"PIC Level", i32 2}
!4 = !{i32 7, !"uwtable", i32 2}
!5 = !{i32 1, !"MaxTLSAlign", i32 65536}
!6 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
