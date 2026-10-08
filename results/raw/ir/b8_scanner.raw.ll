; ModuleID = 'benchmarks\b8_scanner.c'
source_filename = "benchmarks\\b8_scanner.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @count_tokens(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i8, align 1
  store ptr %0, ptr %2, align 8
  store i32 0, ptr %3, align 4
  store i32 0, ptr %4, align 4
  store i32 0, ptr %5, align 4
  br label %7

7:                                                ; preds = %41, %1
  %8 = load ptr, ptr %2, align 8
  %9 = load i32, ptr %5, align 4
  %10 = sext i32 %9 to i64
  %11 = getelementptr inbounds i8, ptr %8, i64 %10
  %12 = load i8, ptr %11, align 1
  %13 = sext i8 %12 to i32
  %14 = icmp ne i32 %13, 0
  br i1 %14, label %15, label %44

15:                                               ; preds = %7
  %16 = load ptr, ptr %2, align 8
  %17 = load i32, ptr %5, align 4
  %18 = sext i32 %17 to i64
  %19 = getelementptr inbounds i8, ptr %16, i64 %18
  %20 = load i8, ptr %19, align 1
  store i8 %20, ptr %6, align 1
  %21 = load i8, ptr %6, align 1
  %22 = sext i8 %21 to i32
  %23 = icmp eq i32 %22, 32
  br i1 %23, label %32, label %24

24:                                               ; preds = %15
  %25 = load i8, ptr %6, align 1
  %26 = sext i8 %25 to i32
  %27 = icmp eq i32 %26, 9
  br i1 %27, label %32, label %28

28:                                               ; preds = %24
  %29 = load i8, ptr %6, align 1
  %30 = sext i8 %29 to i32
  %31 = icmp eq i32 %30, 10
  br i1 %31, label %32, label %33

32:                                               ; preds = %28, %24, %15
  store i32 0, ptr %4, align 4
  br label %40

33:                                               ; preds = %28
  %34 = load i32, ptr %4, align 4
  %35 = icmp ne i32 %34, 0
  br i1 %35, label %39, label %36

36:                                               ; preds = %33
  %37 = load i32, ptr %3, align 4
  %38 = add i32 %37, 1
  store i32 %38, ptr %3, align 4
  store i32 1, ptr %4, align 4
  br label %39

39:                                               ; preds = %36, %33
  br label %40

40:                                               ; preds = %39, %32
  br label %41

41:                                               ; preds = %40
  %42 = load i32, ptr %5, align 4
  %43 = add i32 %42, 1
  store i32 %43, ptr %5, align 4
  br label %7, !llvm.loop !7

44:                                               ; preds = %7
  %45 = load i32, ptr %3, align 4
  ret i32 %45
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
