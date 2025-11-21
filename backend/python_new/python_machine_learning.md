# Python机器学习高级指南

## 1. scikit-learn高级应用

### 1.1 高级特征工程与选择

```python
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, PowerTransformer
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif, RFE, RFECV
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 自定义特征转换器
class FeatureEngineer(BaseEstimator, TransformerMixin):
    """自定义特征工程转换器"""
    
    def __init__(self, interaction_features=True, polynomial_features=True, log_transform=True):
        self.interaction_features = interaction_features
        self.polynomial_features = polynomial_features
        self.log_transform = log_transform
        self.feature_names_ = None
    
    def fit(self, X, y=None):
        # 保存原始特征名称
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = X.columns.tolist()
        return self
    
    def transform(self, X):
        # 转换为DataFrame（如果是numpy数组）
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        
        result = X.copy()
        
        # 对数变换
        if self.log_transform:
            for col in X.select_dtypes(include=[np.number]).columns:
                # 确保值都是正数
                if (X[col] > 0).all():
                    result[f'{col}_log'] = np.log(X[col])
        
        # 多项式特征
        if self.polynomial_features:
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                for i, col1 in enumerate(numeric_cols):
                    for col2 in numeric_cols[i+1:]:
                        result[f'{col1}_x_{col2}'] = X[col1] * X[col2]
        
        # 交互特征
        if self.interaction_features:
            categorical_cols = X.select_dtypes(include=['object', 'category']).columns
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                for cat_col in categorical_cols:
                    for num_col in numeric_cols:
                        # 对每个分类变量计算数值特征的统计量
                        stats = X.groupby(cat_col)[num_col].agg(['mean', 'std', 'median']).reset_index()
                        stats.columns = [cat_col, f'{num_col}_mean_by_{cat_col}', 
                                        f'{num_col}_std_by_{cat_col}', f'{num_col}_median_by_{cat_col}']
                        
                        result = pd.merge(result, stats, on=cat_col, how='left')
        
        return result

# 时间序列特征提取器
class TimeSeriesFeatureExtractor(BaseEstimator, TransformerMixin):
    """时间序列特征提取器"""
    
    def __init__(self, window_sizes=[3, 7, 14]):
        self.window_sizes = window_sizes
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        # 假设X是一个时间序列DataFrame，有'date'列和'value'列
        if not isinstance(X, pd.DataFrame) or 'date' not in X.columns or 'value' not in X.columns:
            return X
        
        X = X.copy()
        X['date'] = pd.to_datetime(X['date'])
        X = X.sort_values('date')
        
        # 对每个窗口大小计算滚动统计量
        for window in self.window_sizes:
            X[f'value_rolling_mean_{window}'] = X['value'].rolling(window=window).mean()
            X[f'value_rolling_std_{window}'] = X['value'].rolling(window=window).std()
            X[f'value_rolling_min_{window}'] = X['value'].rolling(window=window).min()
            X[f'value_rolling_max_{window}'] = X['value'].rolling(window=window).max()
        
        # 添加时间特征
        X['day_of_week'] = X['date'].dt.dayofweek
        X['month'] = X['date'].dt.month
        X['quarter'] = X['date'].dt.quarter
        X['year'] = X['date'].dt.year
        
        # 滞后特征
        for lag in range(1, 8):
            X[f'value_lag_{lag}'] = X['value'].shift(lag)
        
        return X

# 特征选择与降维
def advanced_feature_selection(X, y):
    """高级特征选择技术"""
    print("=== 高级特征选择 ===")
    
    # 1. 移除低方差特征
    print("1. 移除低方差特征")
    selector = VarianceThreshold(threshold=0.01)
    X_variance = selector.fit_transform(X)
    
    print(f"原始特征数量: {X.shape[1]}")
    print(f"移除低方差特征后: {X_variance.shape[1]}")
    
    # 2. 单变量统计特征选择
    print("\n2. 单变量统计特征选择")
    selector = SelectKBest(f_classif, k=10)
    X_kbest = selector.fit_transform(X, y)
    
    print(f"选择前10个最佳特征")
    print("选择的特征索引:", selector.get_support(indices=True))
    
    # 3. 递归特征消除 (RFE)
    print("\n3. 递归特征消除 (RFE)")
    estimator = RandomForestClassifier(n_estimators=100, random_state=42)
    selector = RFE(estimator=estimator, n_features_to_select=10, step=1)
    X_rfe = selector.fit_transform(X, y)
    
    print(f"RFE选择后的特征数量: {X_rfe.shape[1]}")
    print("选择的特征索引:", selector.get_support(indices=True))
    
    # 4. 递归特征消除与交叉验证 (RFECV)
    print("\n4. 递归特征消除与交叉验证 (RFECV)")
    estimator = LogisticRegression(max_iter=1000, random_state=42)
    selector = RFECV(estimator=estimator, step=1, cv=5, scoring='accuracy')
    selector.fit(X, y)
    
    print(f"RFECV选择的最佳特征数量: {selector.n_features_}")
    print("选择的特征索引:", selector.get_support(indices=True))
    
    # 5. 基于模型的特征选择
    print("\n5. 基于模型的特征选择")
    estimator = RandomForestClassifier(n_estimators=100, random_state=42)
    estimator.fit(X, y)
    
    # 获取特征重要性
    feature_importances = pd.DataFrame({
        'feature': range(X.shape[1]),
        'importance': estimator.feature_importances_
    })
    
    # 按重要性排序
    feature_importances = feature_importances.sort_values('importance', ascending=False)
    
    # 选择重要性大于阈值的特征
    threshold = 0.01
    selected_features = feature_importances[feature_importances['importance'] > threshold]
    
    print(f"基于模型选择的特征数量: {len(selected_features)}")
    print("前10个重要特征:")
    print(selected_features.head(10))
    
    # 6. 降维技术
    print("\n6. 降维技术")
    
    # 主成分分析 (PCA)
    pca = PCA(n_components=0.95)  # 保留95%的方差
    X_pca = pca.fit_transform(X)
    
    print(f"PCA降维后的特征数量: {X_pca.shape[1]}")
    print(f"解释方差比: {pca.explained_variance_ratio_.sum():.4f}")
    
    # 独立成分分析 (ICA)
    ica = FastICA(n_components=10, random_state=42)
    X_ica = ica.fit_transform(X)
    
    print(f"ICA降维后的特征数量: {X_ica.shape[1]}")
    
    # 截断奇异值分解 (SVD)
    svd = TruncatedSVD(n_components=10, random_state=42)
    X_svd = svd.fit_transform(X)
    
    print(f"SVD降维后的特征数量: {X_svd.shape[1]}")
    print(f"解释方差比: {svd.explained_variance_ratio_.sum():.4f}")
    
    return {
        'X_variance': X_variance,
        'X_kbest': X_kbest,
        'X_rfe': X_rfe,
        'X_pca': X_pca,
        'X_ica': X_ica,
        'X_svd': X_svd,
        'feature_importances': feature_importances,
        'selected_features': selected_features
    }

# 管道构建
def build_ml_pipeline():
    """构建机器学习管道"""
    print("\n=== 构建机器学习管道 ===")
    
    # 生成示例数据
    X, y = datasets.make_classification(
        n_samples=1000, 
        n_features=20, 
        n_informative=10, 
        n_redundant=5, 
        random_state=42
    )
    
    X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
    y = pd.Series(y)
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 1. 基本管道
    print("1. 基本管道")
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    # 训练和评估
    pipe.fit(X_train, y_train)
    score = pipe.score(X_test, y_test)
    print(f"基本管道准确率: {score:.4f}")
    
    # 2. 复杂管道
    print("\n2. 复杂管道")
    pipe = Pipeline([
        ('feature_engineering', FeatureEngineer()),
        ('scaler', StandardScaler()),
        ('feature_selection', SelectKBest(f_classif, k=15)),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # 训练和评估
    pipe.fit(X_train, y_train)
    score = pipe.score(X_test, y_test)
    print(f"复杂管道准确率: {score:.4f}")
    
    # 3. 管道与网格搜索
    print("\n3. 管道与网格搜索")
    
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('feature_selection', SelectKBest(f_classif)),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    # 定义参数网格
    param_grid = {
        'feature_selection__k': [5, 10, 15, 20],
        'classifier__C': [0.01, 0.1, 1.0, 10.0],
        'classifier__penalty': ['l1', 'l2'],
        'classifier__solver': ['liblinear', 'saga']
    }
    
    # 网格搜索
    grid_search = GridSearchCV(
        pipe, param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"最佳参数: {grid_search.best_params_}")
    print(f"最佳得分: {grid_search.best_score_:.4f}")
    print(f"测试集得分: {grid_search.score(X_test, y_test):.4f}")
    
    # 4. 特征联合
    print("\n4. 特征联合")
    
    # 创建不同的特征提取器
    class FeatureExtractor1(BaseEstimator, TransformerMixin):
        def fit(self, X, y=None):
            return self
        
        def transform(self, X):
            if not isinstance(X, pd.DataFrame):
                X = pd.DataFrame(X)
            
            # 提取前几个特征的平方
            result = X.copy()
            for i in range(min(5, X.shape[1])):
                result[f'feature_{i}_square'] = X.iloc[:, i] ** 2
            
            return result
    
    class FeatureExtractor2(BaseEstimator, TransformerMixin):
        def fit(self, X, y=None):
            return self
        
        def transform(self, X):
            if not isinstance(X, pd.DataFrame):
                X = pd.DataFrame(X)
            
            # 提取特征之间的交互
            result = X.copy()
            if X.shape[1] > 1:
                for i in range(min(3, X.shape[1])):
                    for j in range(i+1, min(4, X.shape[1])):
                        result[f'feature_{i}_x_{j}'] = X.iloc[:, i] * X.iloc[:, j]
            
            return result
    
    # 创建特征联合
    combined_features = FeatureUnion([
        ('extractor1', FeatureExtractor1()),
        ('extractor2', FeatureExtractor2())
    ])
    
    # 创建管道
    pipe = Pipeline([
        ('features', combined_features),
        ('scaler', StandardScaler()),
        ('classifier', GradientBoostingClassifier(random_state=42))
    ])
    
    # 训练和评估
    pipe.fit(X_train, y_train)
    score = pipe.score(X_test, y_test)
    print(f"特征联合管道准确率: {score:.4f}")
    
    return pipe, grid_search

# 高级模型评估
def advanced_model_evaluation():
    """高级模型评估技术"""
    print("\n=== 高级模型评估 ===")
    
    # 生成示例数据
    X, y = datasets.make_classification(
        n_samples=1000, 
        n_features=20, 
        n_informative=10, 
        n_redundant=5, 
        random_state=42
    )
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 创建多个模型
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42)
    }
    
    # 1. 交叉验证评估
    print("1. 交叉验证评估")
    
    results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        results[name] = scores
        
        print(f"{name}: {scores.mean():.4f} (±{scores.std():.4f})")
    
    # 可视化结果
    plt.figure(figsize=(10, 6))
    plt.boxplot(list(results.values()), labels=list(results.keys()))
    plt.title('模型交叉验证准确率比较')
    plt.ylabel('准确率')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # 2. 学习曲线
    print("\n2. 学习曲线分析")
    
    from sklearn.model_selection import learning_curve
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, (name, model) in enumerate(models.items()):
        train_sizes, train_scores, test_scores = learning_curve(
            model, X, y, cv=5, n_jobs=-1, 
            train_sizes=np.linspace(0.1, 1.0, 10),
            scoring='accuracy'
        )
        
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)
        
        axes[i].plot(train_sizes, train_mean, 'o-', color='blue', label='训练集')
        axes[i].fill_between(train_sizes, train_mean + train_std, train_mean - train_std, alpha=0.1, color='blue')
        
        axes[i].plot(train_sizes, test_mean, 'o-', color='red', label='验证集')
        axes[i].fill_between(train_sizes, test_mean + test_std, test_mean - test_std, alpha=0.1, color='red')
        
        axes[i].set_title(f'{name} 学习曲线')
        axes[i].set_xlabel('训练样本数')
        axes[i].set_ylabel('准确率')
        axes[i].legend(loc='best')
        axes[i].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # 3. 验证曲线
    print("\n3. 验证曲线分析")
    
    from sklearn.model_selection import validation_curve
    
    # 选择一个模型进行分析
    model = RandomForestClassifier(random_state=42)
    param_name = 'n_estimators'
    param_range = [10, 50, 100, 150, 200]
    
    train_scores, test_scores = validation_curve(
        model, X, y, param_name=param_name, param_range=param_range,
        cv=5, scoring='accuracy', n_jobs=-1
    )
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(param_range, train_mean, 'o-', color='blue', label='训练集')
    plt.fill_between(param_range, train_mean + train_std, train_mean - train_std, alpha=0.1, color='blue')
    
    plt.plot(param_range, test_mean, 'o-', color='red', label='验证集')
    plt.fill_between(param_range, test_mean + test_std, test_mean - test_std, alpha=0.1, color='red')
    
    plt.title('随机森林验证曲线')
    plt.xlabel('n_estimators')
    plt.ylabel('准确率')
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()
    
    # 4. 混淆矩阵和分类报告
    print("\n4. 混淆矩阵和分类报告")
    
    from sklearn.metrics import confusion_matrix, classification_report
    
    # 训练模型
    model = models['Random Forest']
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('混淆矩阵')
    plt.ylabel('真实标签')
    plt.xlabel('预测标签')
    plt.show()
    
    # 分类报告
    print("分类报告:")
    print(classification_report(y_test, y_pred))
    
    # 5. ROC曲线
    print("\n5. ROC曲线分析")
    
    from sklearn.metrics import roc_curve, auc
    
    plt.figure(figsize=(10, 8))
    
    for name, model in models.items():
        try:
            # 获取预测概率
            if hasattr(model, "predict_proba"):
                y_scores = model.fit(X_train, y_train).predict_proba(X_test)[:, 1]
            else:
                # 对于没有predict_proba的模型，使用decision_function
                y_scores = model.fit(X_train, y_train).decision_function(X_test)
            
            # 计算ROC曲线
            fpr, tpr, _ = roc_curve(y_test, y_scores)
            roc_auc = auc(fpr, tpr)
            
            plt.plot(fpr, tpr, label=f'{name} (AUC = {roc_auc:.3f})')
        except:
            pass
    
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('假正率')
    plt.ylabel('真正率')
    plt.title('ROC曲线')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.show()
    
    return results

# 运行示例
def demo_sklearn_advanced():
    """演示scikit-learn高级应用"""
    print("=== scikit-learn高级应用演示 ===")
    
    # 1. 高级特征工程
    print("\n1. 高级特征工程")
    
    # 生成示例数据
    X, y = datasets.make_classification(
        n_samples=1000, 
        n_features=20, 
        n_informative=10, 
        n_redundant=5, 
        random_state=42
    )
    
    X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
    
    # 应用自定义特征工程
    fe = FeatureEngineer()
    X_fe = fe.fit_transform(X)
    
    print(f"原始特征数量: {X.shape[1]}")
    print(f"特征工程后特征数量: {X_fe.shape[1]}")
    
    # 2. 高级特征选择
    selection_results = advanced_feature_selection(X, y)
    
    # 3. 构建机器学习管道
    pipe, grid_search = build_ml_pipeline()
    
    # 4. 高级模型评估
    eval_results = advanced_model_evaluation()
    
    print("\n所有scikit-learn高级应用演示完成!")

# 运行演示
if __name__ == "__main__":
    demo_sklearn_advanced()
```

### 1.2 集成学习高级技术

```python
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, 
    VotingClassifier, BaggingClassifier, ExtraTreesClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.classifier import StackingClassifier, EnsembleVoteClassifier
import warnings
warnings.filterwarnings('ignore')

# 基础集成方法比较
def compare_ensemble_methods():
    """比较不同集成学习方法"""
    print("=== 比较不同集成学习方法 ===")
    
    # 生成示例数据
    X, y = datasets.make_classification(
        n_samples=1000, 
        n_features=20, 
        n_informative=10, 
        n_redundant=5, 
        random_state=42
    )
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 定义基础模型
    base_models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Extra Trees': ExtraTreesClassifier(n_estimators=100, random_state=42),
        'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    # 评估模型
    results = {}
    
    for name, model in base_models.items():
        # 训练模型
        model.fit(X_train, y_train)
        
        # 预测
        y_pred = model.predict(X_test)
        y_prob = None
        
        try:
            y_prob = model.predict_proba(X_test)[:, 1]
        except:
            pass
        
        # 评估
        accuracy = accuracy_score(y_test, y_pred)
        auc = None
        
        if y_prob is not None:
            auc = roc_auc_score(y_test, y_prob)
        
        results[name] = {'accuracy': accuracy, 'auc': auc}
        
        print(f"{name}: 准确率={accuracy:.4f}, AUC={auc:.4f if auc else 'N/A'}")
    
    # 可视化结果
    metrics = ['accuracy', 'auc']
    values = {metric: [] for metric in metrics}
    names = []
    
    for name, result in results.items():
        names.append(name)
        for metric in metrics:
            values[metric].append(result[metric] if result[metric] else 0)
    
    # 绘制条形图
    x = np.arange(len(names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, values['accuracy'], width, label='准确率')
    ax.bar(x + width/2, values['auc'], width, label='AUC')
    
    ax.set_xlabel('模型')
    ax.set_ylabel('性能指标')
    ax.set_title('不同集成学习方法比较')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45)
    ax.legend()
    
    plt.tight_layout()
    plt.show()
    
    return results

# 高级集成技术：混合与堆叠
def advanced_ensemble_techniques():
    """高级集成技术：混合与堆叠"""
    print("\n=== 高级集成技术：混合与堆叠 ===")
    
    # 生成示例数据
    X, y = datasets.make_classification(
        n_samples=1000, 
        n_features=20, 
        n_informative=10, 
        n_redundant=5, 
        random_state=42
    )
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 1. 简单平均/投票
    print("1. 简单平均/投票")
    
    # 定义基础模型
    clf1 = LogisticRegression(random_state=42)
    clf2 = RandomForestClassifier(random_state=42)
    clf3 = GradientBoostingClassifier(random_state=42)
    
    # 创建投票分类器
    eclf1 = VotingClassifier(estimators=[
        ('lr', clf1), ('rf', clf2), ('gb', clf3)], voting='hard')
    
    eclf2 = VotingClassifier(estimators=[
        ('lr', clf1), ('rf', clf2), ('gb', clf3)], voting='soft')
    
    # 训练和评估
    models = {
        'Logistic Regression': clf1,
        'Random Forest': clf2,
        'Gradient Boosting': clf3,
        'Hard Voting': eclf1,
        'Soft Voting': eclf2
    }
    
    results = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        results[name] = {'accuracy': accuracy}
        
        print(f"{name}: 准确率={accuracy:.4f}")
    
    # 2. 堆叠集成
    print("\n2. 堆叠集成")
    
    # 使用mlxtend的StackingClassifier
    sclf = StackingClassifier(
        classifiers=[clf1, clf2, clf3], 
        meta_classifier=LogisticRegression(random_state=42)
    )
    
    sclf.fit(X_train, y_train)
    y_pred = sclf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    results['Stacking'] = {'accuracy': accuracy}
    print(f"Stacking: 准确率={accuracy:.4f}")
    
    # 3. 混合集成 (Blending)
    print("\n3. 混合集成 (Blending)")
    
    # 分割训练集为训练和验证集
    X_train_main, X_val, y_train_main, y_val = train_test_split(
        X_train, y_train, test_size=0.3, random_state=42
    )
    
    # 训练基础模型
    clf1.fit(X_train_main, y_train_main)
    clf2.fit(X_train_main, y_train_main)
    clf3.fit(X_train_main, y_train_main)
    
    # 获取基础模型的预测结果作为新特征
    val_pred1 = clf1.predict_proba(X_val)[:, 1]
    val_pred2 = clf2.predict_proba(X_val)[:, 1]
    val_pred3 = clf3.predict_proba(X_val)[:, 1]
    
    # 训练元模型
    meta_X = np.column_stack((val_pred1, val_pred2, val_pred3))
    meta_model = LogisticRegression(random_state=42)
    meta_model.fit(meta_X, y_val)
    
    # 获取测试集的预测结果
    test_pred1 = clf1.predict_proba(X_test)[:, 1]
    test_pred2 = clf2.predict_proba(X_test)[:, 1]
    test_pred3 = clf3.predict_proba(X_test)[:, 1]
    
    meta_test_X = np.column_stack((test_pred1, test_pred2, test_pred3))
    y_pred = meta_model.predict(meta_test_X)
    
    accuracy = accuracy_score(y_test, y_pred)
    
    results['Blending'] = {'accuracy': accuracy}
    print(f"Blending: 准确率={accuracy:.4f}")
    
    # 4. 自定义加权集成
    print("\n4. 自定义加权集成")
    
    # 训练基础模型
    clf1.fit(X_train, y_train)
    clf2.fit(X_train, y_train)
    clf3.fit(X_train, y_train)
    
    # 获取预测概率
    pred1 = clf1.predict_proba(X_test)[:, 1]
    pred2 = clf2.predict_proba(X_test)[:, 1]
    pred3 = clf3.predict_proba(X_test)[:, 1]
    
    # 定义权重
    weights = [0.2, 0.3, 0.5]  # 可以基于验证性能调整
    
    # 加权平均
    weighted_pred = weights[0] * pred1 + weights[1] * pred2 + weights[2] * pred3
    y_pred = (weighted_pred > 0.5).astype(int)
    
    accuracy = accuracy_score(y_test, y_pred)
    
    results['Weighted Average'] = {'accuracy': accuracy}
    print(f"Weighted Average: 准确率={accuracy:.4f}")
    
    # 5. 多级集成
    print("\n5. 多级集成")
    
    # 第一级集成
    level1_clf1 = RandomForestClassifier(n_estimators=50, random_state=42)
    level1_clf2 = GradientBoostingClassifier(n_estimators=50, random_state=42)
    level1_clf3 = ExtraTreesClassifier(n_estimators=50, random_state=42)
    
    # 第一级集成使用投票
    level1_voting = VotingClassifier([
        ('rf', level1_clf1), 
        ('gb', level1_clf2), 
        ('et', level1_clf3)
    ], voting='soft')
    
    level1_voting.fit(X_train, y_train)
    level1_pred = level1_voting.predict_proba(X_test)[:, 1]
    
    # 第二级集成
    level2_clf1 = LogisticRegression(random_state=42)
    level2_clf2 = SVC(probability=True, random_state=42)
    level2_clf3 = KNeighborsClassifier()
    
    level2_clf1.fit(X_train, y_train)
    level2_clf2.fit(X_train, y_train)
    level2_clf3.fit(X_train, y_train)
    
    level2_pred1 = level2_clf1.predict_proba(X_test)[:, 1]
    level2_pred2 = level2_clf2.predict_proba(X_test)[:, 1]
    level2_pred3 = level2_clf3.predict_proba(X_test)[:, 1]
    
    # 元模型
    meta_X = np.column_stack((level1_pred, level2_pred1, level2_pred2, level2_pred3))
    meta_model = LogisticRegression(random_state=42)
    meta_model.fit(meta_X, y_test)  # 注意: 这里使用测试集训练，仅作示例
    
    y_pred = meta_model.predict(meta_X)
    accuracy = accuracy_score(y_test, y_pred)
    
    results['Multi-level Ensemble'] = {'accuracy': accuracy}
    print(f"Multi-level Ensemble: 准确率={accuracy:.4f}")
    
    # 可视化结果
    names = list(results.keys())
    values = [result['accuracy'] for result in results.values()]
    
    plt.figure(figsize=(12, 6))
    plt.barh(names, values)
    plt.xlabel('准确率')
    plt.title('不同集成技术比较')
    plt.xlim(0, 1)
    for i, v in enumerate(values):
        plt.text(v + 0.01, i - 0.05, f'{v:.4f}')
    
    plt.tight_layout()
    plt.show()
    
    return results

# 动态集成方法
def dynamic_ensemble_methods():
    """动态集成方法"""
    print("\n=== 动态集成方法 ===")
    
    # 生成示例数据
    X, y = datasets.make_classification(
        n_samples=1000, 
        n_features=20, 
        n_informative=10, 
        n_redundant=5, 
        random_state=42
    )
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 1. 动态选择集成 (DSE)
    print("1. 动态选择集成 (DSE)")
    
    # 定义基础模型
    models = [
        ('lr', LogisticRegression(random_state=42)),
        ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
        ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
        ('svm', SVC(probability=True, random_state=42)),
        ('knn', KNeighborsClassifier())
    ]
    
    # 训练所有模型
    for name, model in models:
        model.fit(X_train, y_train)
    
    # 对每个测试样本动态选择最佳模型
    def dynamic_selection_predict(X_test, models, X_val, y_val, k=3):
        """动态选择集成预测"""
        predictions = []
        
        for x in X_test:
            # 计算每个模型与当前样本的相似度
            similarities = []
            local_accuracies = []
            
            for name, model in models:
                # 获取验证集上的预测
                y_pred = model.predict(X_val)
                accuracy = accuracy_score(y_val, y_pred)
                
                # 计算当前样本与验证集的相似度
                # 这里使用简单的k近邻相似度
                from sklearn.neighbors import NearestNeighbors
                nbrs = NearestNeighbors(n_neighbors=5).fit(X_val)
                distances, indices = nbrs.kneighbors([x])
                local_accuracy = np.mean(y_pred[indices[0]] == y_val[indices[0]])
                
                similarities.append(local_accuracy)
                local_accuracies.append(accuracy)
            
            # 选择表现最好的k个模型
            indices = np.argsort(similarities)[-k:]
            
            # 对选中的模型进行投票
            votes = []
            for idx in indices:
                name, model = models[idx]
                pred = model.predict([x])[0]
                votes.append(pred)
            
            # 多数投票
            pred = np.bincount(votes).argmax()
            predictions.append(pred)
        
        return np.array(predictions)
    
    # 获取一部分训练数据作为验证集
    X_main, X_val, y_main, y_val = train_test_split(
        X_train, y_train, test_size=0.3, random_state=42
    )
    
    # 重新训练模型
    for name, model in models:
        model.fit(X_main, y_main)
    
    # 动态选择预测
    dse_pred = dynamic_selection_predict(X_test, models, X_val, y_val, k=3)
    dse_accuracy = accuracy_score(y_test, dse_pred)
    
    print(f"动态选择集成准确率: {dse_accuracy:.4f}")
    
    # 2. 动态集成选择 (DES)
    print("\n2. 动态集成选择 (DES)")
    
    def des_predict(X_test, models, X_val, y_val, k=5):
        """动态集成选择预测"""
        predictions = []
        
        for x in X_test:
            # 获取验证集上的预测概率
            probas = []
            for name, model in models:
                try:
                    y_proba = model.predict_proba(X_val)
                    probas.append(y_proba)
                except:
                    # 对于没有predict_proba的模型
                    y_pred = model.predict(X_val)
                    y_proba = np.zeros((len(y_pred), 2))
                    y_proba[np.arange(len(y_pred)), y_pred] = 1
                    probas.append(y_proba)
            
            # 计算每个样本与x的相似度
            from sklearn.neighbors import NearestNeighbors
            nbrs = NearestNeighbors(n_neighbors=5).fit(X_val)
            distances, indices = nbrs.kneighbors([x])
            
            # 计算每个模型在邻域上的性能
            competences = []
            for i, (name, model) in enumerate(models):
                y_pred = model.predict(X_val[indices[0]])
                competence = accuracy_score(y_val[indices[0]], y_pred)
                competences.append(competence)
            
            # 选择表现最好的k个模型
            selected_models = [models[i] for i in np.argsort(competences)[-k:]]
            
            # 加权平均
            weights = np.array([competences[i] for i in np.argsort(competences)[-k:]])
            weights = weights / weights.sum()
            
            # 获取加权平均的预测
            ensemble_proba = np.zeros(2)
            for i, (name, model) in enumerate(selected_models):
                try:
                    proba = model.predict_proba([x])[0]
                    ensemble_proba += weights[i] * proba
                except:
                    pred = model.predict([x])[0]
                    ensemble_proba[pred] += weights[i]
            
            pred = ensemble_proba.argmax()
            predictions.append(pred)
        
        return np.array(predictions)
    
    # DES预测
    des_pred = des_predict(X_test, models, X_val, y_val, k=3)
    des_accuracy = accuracy_score(y_test, des_pred)
    
    print(f"动态集成选择准确率: {des_accuracy:.4f}")
    
    # 3. 自适应集成选择 (AEC)
    print("\n3. 自适应集成选择 (AEC)")
    
    def aec_predict(X_test, models, X_val, y_val, m=5):
        """自适应集成选择预测"""
        predictions = []
        
        for x in X_test:
            # 计算每个模型与当前样本的相似度
            competences = []
            
            for name, model in models:
                # 计算当前样本与验证集的相似度
                from sklearn.neighbors import NearestNeighbors
                nbrs = NearestNeighbors(n_neighbors=m).fit(X_val)
                distances, indices = nbrs.kneighbors([x])
                
                # 计算模型在邻域上的性能
                y_pred = model.predict(X_val[indices[0]])
                competence = accuracy_score(y_val[indices[0]], y_pred)
                competences.append(competence)
            
            # 根据性能选择模型
            if max(competences) > 0.7:  # 高性能阈值
                best_idx = np.argmax(competences)
                pred = models[best_idx][1].predict([x])[0]
            else:  # 使用投票
                selected_models = [models[i] for i in np.argsort(competences)[-3:]]
                votes = [model.predict([x])[0] for _, model in selected_models]
                pred = np.bincount(votes).argmax()
            
            predictions.append(pred)
        
        return np.array(predictions)
    
    # AEC预测
    aec_pred = aec_predict(X_test, models, X_val, y_val, m=5)
    aec_accuracy = accuracy_score(y_test, aec_pred)
    
    print(f"自适应集成选择准确率: {aec_accuracy:.4f}")
    
    # 比较结果
    results = {
        'Dynamic Selection': dse_accuracy,
        'Dynamic Ensemble Selection': des_accuracy,
        'Adaptive Ensemble Selection': aec_accuracy
    }
    
    # 可视化结果
    names = list(results.keys())
    values = list(results.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(names, values)
    plt.xlabel('方法')
    plt.ylabel('准确率')
    plt.title('动态集成方法比较')
    plt.ylim(0, 1)
    for i, v in enumerate(values):
        plt.text(i - 0.1, v + 0.01, f'{v:.4f}')
    
    plt.tight_layout()
    plt.show()
    
    return results

# 运行示例
def demo_ensemble_learning():
    """演示集成学习高级技术"""
    print("=== 集成学习高级技术演示 ===")
    
    # 1. 比较不同集成学习方法
    ensemble_results = compare_ensemble_methods()
    
    # 2. 高级集成技术
    advanced_results = advanced_ensemble_techniques()
    
    # 3. 动态集成方法
    dynamic_results = dynamic_ensemble_methods()
    
    print("\n所有集成学习高级技术演示完成!")

# 运行演示
if __name__ == "__main__":
    demo_ensemble_learning()
```

## 2. 深度学习框架集成

### 2.1 TensorFlow高级应用

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks, utils, optimizers
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# 自定义TensorFlow层
class AttentionLayer(layers.Layer):
    """自定义注意力层"""
    
    def __init__(self, units=32, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        self.units = units
    
    def build(self, input_shape):
        # 为每个输入创建权重矩阵
        self.W = self.add_weight(
            shape=(input_shape[-1], self.units),
            initializer='glorot_uniform',
            trainable=True,
            name='W'
        )
        
        self.b = self.add_weight(
            shape=(self.units,),
            initializer='zeros',
            trainable=True,
            name='b'
        )
        
        self.u = self.add_weight(
            shape=(self.units,),
            initializer='glorot_uniform',
            trainable=True,
            name='u'
        )
        
        super(AttentionLayer, self).build(input_shape)
    
    def call(self, inputs, mask=None):
        # 计算注意力分数
        uit = tf.nn.tanh(tf.tensordot(inputs, self.W, axes=1) + self.b)
        
        ait = tf.tensordot(uit, self.u, axes=1)
        ait = tf.squeeze(ait, -1)
        
        # 应用掩码（如果有）
        if mask is not None:
            ait -= 1e9 * (1 - tf.cast(mask, tf.float32))
        
        # 计算注意力权重
        ait = tf.nn.softmax(ait)
        ait = tf.expand_dims(ait, -1)
        
        # 应用注意力权重
        weighted_input = inputs * ait
        output = tf.reduce_sum(weighted_input, axis=1)
        
        return output
    
    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[2])

# 残差块
class ResidualBlock(layers.Layer):
    """自定义残差块"""
    
    def __init__(self, filters, kernel_size=3, stride=1, **kwargs):
        super(ResidualBlock, self).__init__(**kwargs)
        self.filters = filters
        self.kernel_size = kernel_size
        self.stride = stride
        
        # 定义层
        self.conv1 = layers.Conv2D(filters, kernel_size, strides=stride, 
                                  padding='same', kernel_initializer='he_normal')
        self.bn1 = layers.BatchNormalization()
        self.relu1 = layers.ReLU()
        
        self.conv2 = layers.Conv2D(filters, kernel_size, padding='same',
                                  kernel_initializer='he_normal')
        self.bn2 = layers.BatchNormalization()
        
        # 跳跃连接
        self.shortcut_conv = None
        if stride != 1:
            self.shortcut_conv = layers.Conv2D(filters, 1, strides=stride,
                                            padding='same', kernel_initializer='he_normal')
            self.shortcut_bn = layers.BatchNormalization()
        
        self.relu2 = layers.ReLU()
    
    def call(self, inputs, training=None):
        # 主路径
        x = self.conv1(inputs)
        x = self.bn1(x, training=training)
        x = self.relu1(x)
        
        x = self.conv2(x)
        x = self.bn2(x, training=training)
        
        # 跳跃连接
        shortcut = inputs
        if self.stride != 1:
            shortcut = self.shortcut_conv(shortcut)
            shortcut = self.shortcut_bn(shortcut, training=training)
        
        # 残差连接
        x = x + shortcut
        x = self.relu2(x)
        
        return x

# 自定义激活函数
class Swish(layers.Layer):
    """自定义Swish激活函数"""
    
    def __init__(self, **kwargs):
        super(Swish, self).__init__(**kwargs)
        self.beta = self.add_weight(
            shape=(),
            initializer='ones',
            trainable=True,
            name='beta'
        )
    
    def call(self, inputs):
        return inputs * tf.nn.sigmoid(self.beta * inputs)

# 自定义损失函数
def focal_loss(gamma=2., alpha=.25):
    """Focal Loss 用于处理类别不平衡问题"""
    
    def loss(y_true, y_pred):
        y_pred = tf.clip_by_value(y_pred, tf.keras.backend.epsilon(), 1. - tf.keras.backend.epsilon())
        
        # 计算交叉熵
        cross_entropy = -y_true * tf.math.log(y_pred)
        
        # 计算权重
        weight = alpha * tf.pow(1 - y_pred, gamma)
        
        return tf.reduce_sum(weight * cross_entropy, axis=-1)
    
    return loss

# 自定义指标
def f1_score(y_true, y_pred):
    """计算F1分数"""
    true_positives = tf.reduce_sum(tf.round(tf.clip_by_value(y_true * y_pred, 0, 1)))
    predicted_positives = tf.reduce_sum(tf.round(tf.clip_by_value(y_pred, 0, 1)))
    possible_positives = tf.reduce_sum(tf.round(tf.clip_by_value(y_true, 0, 1)))
    
    precision = true_positives / (predicted_positives + tf.keras.backend.epsilon())
    recall = true_positives / (possible_positives + tf.keras.backend.epsilon())
    
    f1_val = 2 * (precision * recall) / (precision + recall + tf.keras.backend.epsilon())
    return f1_val

# 自定义回调函数
class CustomCallback(callbacks.Callback):
    """自定义回调函数，用于监控和调整训练过程"""
    
    def __init__(self, validation_data=None, patience=5):
        super(CustomCallback, self).__init__()
        self.validation_data = validation_data
        self.patience = patience
        self.wait = 0
        self.best_loss = float('inf')
        self.lr_schedule = [0.001, 0.0005, 0.0001, 0.00005]
        self.current_lr_idx = 0
    
    def on_train_begin(self, logs=None):
        print("训练开始")
    
    def on_train_end(self, logs=None):
        print("训练结束")
    
    def on_epoch_begin(self, epoch, logs=None):
        print(f"Epoch {epoch+1} 开始")
    
    def on_epoch_end(self, epoch, logs=None):
        val_loss = logs.get('val_loss')
        
        # 如果有验证数据，检查是否需要调整学习率
        if val_loss is not None:
            if val_loss < self.best_loss:
                self.best_loss = val_loss
                self.wait = 0
            else:
                self.wait += 1
                if self.wait >= self.patience and self.current_lr_idx < len(self.lr_schedule) - 1:
                    self.current_lr_idx += 1
                    new_lr = self.lr_schedule[self.current_lr_idx]
                    tf.keras.backend.set_value(self.model.optimizer.lr, new_lr)
                    print(f"\n降低学习率至 {new_lr}")
                    self.wait = 0

# 构建自定义模型
def build_custom_model(input_shape, num_classes):
    """构建自定义神经网络模型"""
    
    # 输入层
    inputs = keras.Input(shape=input_shape)
    
    # 第一个卷积块
    x = layers.Conv2D(32, 3, padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = Swish()(x)
    x = layers.MaxPooling2D(2)(x)
    
    # 残差块
    x = ResidualBlock(64, stride=2)(x)
    x = ResidualBlock(64)(x)
    
    # 第二个卷积块
    x = ResidualBlock(128, stride=2)(x)
    x = ResidualBlock(128)(x)
    
    # 全局平均池化
    x = layers.GlobalAveragePooling2D()(x)
    
    # 全连接层
    x = layers.Dense(256)(x)
    x = layers.BatchNormalization()(x)
    x = Swish()(x)
    x = layers.Dropout(0.5)(x)
    
    # 输出层
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    # 创建模型
    model = keras.Model(inputs=inputs, outputs=outputs)
    
    return model

# 构建基于注意力的模型
def build_attention_model(input_shape, num_classes):
    """构建基于注意力的模型"""
    
    # 输入层
    inputs = keras.Input(shape=input_shape)
    
    # 特征提取
    x = layers.Conv2D(32, 3, padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D(2)(x)
    
    x = layers.Conv2D(64, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D(2)(x)
    
    # 重塑为序列以应用注意力
    # 假设输入形状为 (height, width, channels)
    height, width, channels = input_shape
    pooled_size = (height // 4, width // 4)
    x = layers.Reshape((pooled_size[0] * pooled_size[1], 64))(x)
    
    # 应用注意力
    x = AttentionLayer(32)(x)
    
    # 全连接层
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    
    # 输出层
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    # 创建模型
    model = keras.Model(inputs=inputs, outputs=outputs)
    
    return model

# 模型训练与评估
def train_and_evaluate_model(X_train, y_train, X_test, y_test, model_type='custom'):
    """训练和评估模型"""
    
    # 根据模型类型构建模型
    if model_type == 'custom':
        model = build_custom_model(X_train.shape[1:], y_train.shape[1])
    elif model_type == 'attention':
        model = build_attention_model(X_train.shape[1:], y_train.shape[1])
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # 编译模型
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy', f1_score]
    )
    
    # 打印模型摘要
    print(f"模型类型: {model_type}")
    model.summary()
    
    # 定义回调
    callback_list = [
        callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-7),
        callbacks.ModelCheckpoint(
            f'best_{model_type}_model.h5', 
            save_best_only=True,
            monitor='val_accuracy'
        ),
        CustomCallback(validation_data=(X_test, y_test))
    ]
    
    # 训练模型
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=50,
        batch_size=32,
        callbacks=callback_list,
        verbose=1
    )
    
    # 评估模型
    y_pred = np.argmax(model.predict(X_test), axis=1)
    y_true = np.argmax(y_test, axis=1)
    
    accuracy = accuracy_score(y_true, y_pred)
    print(f"测试集准确率: {accuracy:.4f}")
    print("分类报告:")
    print(classification_report(y_true, y_pred))
    
    # 可视化训练过程
    plt.figure(figsize=(12, 5))
    
    # 准确率曲线
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='训练准确率')
    plt.plot(history.history['val_accuracy'], label='验证准确率')
    plt.title('模型准确率')
    plt.xlabel('Epoch')
    plt.ylabel('准确率')
    plt.legend()
    plt.grid(True)
    
    # 损失曲线
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='训练损失')
    plt.plot(history.history['val_loss'], label='验证损失')
    plt.title('模型损失')
    plt.xlabel('Epoch')
    plt.ylabel('损失')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    return model, history

# 迁移学习
def transfer_learning(X_train, y_train, X_test, y_test):
    """使用迁移学习"""
    
    # 加载预训练模型
    base_model = keras.applications.ResNet50(
        include_top=False,
        weights='imagenet',
        input_shape=X_train.shape[1:]
    )
    
    # 冻结预训练模型的所有层
    base_model.trainable = False
    
    # 创建自定义顶部
    inputs = keras.Input(shape=X_train.shape[1:])
    
    # 预处理（特定于预训练模型）
    x = keras.applications.resnet.preprocess_input(inputs)
    
    # 通过预训练模型
    x = base_model(x, training=False)
    
    # 添加自定义层
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    
    # 输出层
    outputs = layers.Dense(y_train.shape[1], activation='softmax')(x)
    
    # 创建模型
    model = keras.Model(inputs, outputs)
    
    # 编译模型
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("迁移学习模型:")
    model.summary()
    
    # 第一阶段训练（仅训练新添加的层）
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=10,
        batch_size=32
    )
    
    # 解冻预训练模型的一部分
    base_model.trainable = True
    
    # 选择解冻的层（解冻最后10层）
    for layer in base_model.layers[:-10]:
        layer.trainable = False
    
    # 重新编译模型（使用较低的学习率）
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # 第二阶段训练（微调）
    history_fine = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=20,
        batch_size=32
    )
    
    # 评估模型
    y_pred = np.argmax(model.predict(X_test), axis=1)
    y_true = np.argmax(y_test, axis=1)
    
    accuracy = accuracy_score(y_true, y_pred)
    print(f"迁移学习测试集准确率: {accuracy:.4f}")
    
    return model, history, history_fine

# 运行示例
def demo_tensorflow_advanced():
    """演示TensorFlow高级应用"""
    
    print("=== TensorFlow高级应用演示 ===")
    
    # 创建模拟数据
    # 这里使用随机数据，实际应用中应该使用真实数据集
    # 为了演示，我们假设使用CIFAR-10形状的数据
    X_train = np.random.rand(1000, 32, 32, 3)
    y_train = keras.utils.to_categorical(np.random.randint(0, 10, 1000), 10)
    X_test = np.random.rand(200, 32, 32, 3)
    y_test = keras.utils.to_categorical(np.random.randint(0, 10, 200), 10)
    
    # 1. 训练自定义模型
    print("\n1. 训练自定义模型")
    custom_model, custom_history = train_and_evaluate_model(
        X_train, y_train, X_test, y_test, 'custom'
    )
    
    # 2. 训练注意力模型
    print("\n2. 训练注意力模型")
    attention_model, attention_history = train_and_evaluate_model(
        X_train, y_train, X_test, y_test, 'attention'
    )
    
    # 3. 迁移学习
    print("\n3. 迁移学习")
    transfer_model, history, history_fine = transfer_learning(
        X_train, y_train, X_test, y_test
    )
    
    print("\n所有TensorFlow高级应用演示完成!")
    return custom_model, attention_model, transfer_model

# 运行演示
if __name__ == "__main__":
    demo_tensorflow_advanced()
```

### 2.2 PyTorch高级应用

```python
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torchvision import transforms, models
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 自定义PyTorch层
class AttentionModule(nn.Module):
    """自定义注意力模块"""
    
    def __init__(self, in_features, out_features):
        super(AttentionModule, self).__init__()
        self.W = nn.Linear(in_features, out_features, bias=False)
        self.u = nn.Linear(out_features, 1, bias=False)
        self.tanh = nn.Tanh()
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        # x shape: (batch_size, seq_len, in_features)
        
        # 计算注意力分数
        uit = self.tanh(self.W(x))  # (batch_size, seq_len, out_features)
        ait = self.u(uit).squeeze(2)  # (batch_size, seq_len)
        
        # 计算注意力权重
        ait = self.softmax(ait)
        ait = ait.unsqueeze(2)  # (batch_size, seq_len, 1)
        
        # 应用注意力权重
        weighted_input = x * ait
        output = torch.sum(weighted_input, dim=1)  # (batch_size, in_features)
        
        return output

# 残差块
class ResidualBlock(nn.Module):
    """自定义残差块"""
    
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                               stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.downsample = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        identity = self.downsample(identity)
        
        out += identity
        out = self.relu(out)
        
        return out

# 自定义激活函数
class Swish(nn.Module):
    """自定义Swish激活函数"""
    
    def __init__(self, beta=1.0):
        super(Swish, self).__init__()
        self.beta = nn.Parameter(torch.tensor([beta], dtype=torch.float32))
    
    def forward(self, x):
        return x * torch.sigmoid(self.beta * x)

# 自定义数据集类
class CustomDataset(Dataset):
    """自定义数据集类"""
    
    def __init__(self, X, y, transform=None):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
        self.transform = transform
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        sample = self.X[idx]
        label = self.y[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample, label

# 自定义模型
class CustomCNN(nn.Module):
    """自定义CNN模型"""
    
    def __init__(self, num_classes=10):
        super(CustomCNN, self).__init__()
        
        # 特征提取
        self.features = nn.Sequential(
            # 第一块
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            Swish(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # 第二块
            ResidualBlock(64, 128, stride=2),
            ResidualBlock(128, 128),
            
            # 第三块
            ResidualBlock(128, 256, stride=2),
            ResidualBlock(256, 256),
            
            # 第四块
            ResidualBlock(256, 512, stride=2),
            ResidualBlock(512, 512),
        )
        
        # 分类器
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            Swish(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# 基于注意力的模型
class AttentionCNN(nn.Module):
    """基于注意力的CNN模型"""
    
    def __init__(self, num_classes=10):
        super(AttentionCNN, self).__init__()
        
        # 特征提取
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            Swish(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            Swish(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        
        # 注意力模块
        self.attention = AttentionModule(64, 32)
        
        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(64, 128),
            Swish(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        # 特征提取
        x = self.features(x)
        
        # 获取形状以便处理
        batch_size, channels, height, width = x.size()
        
        # 重塑为序列以应用注意力
        x = x.permute(0, 2, 3, 1)  # (batch_size, height, width, channels)
        x = x.reshape(batch_size, -1, channels)  # (batch_size, height*width, channels)
        
        # 应用注意力
        x = self.attention(x)  # (batch_size, channels)
        
        # 分类
        x = self.classifier(x)
        
        return x

# 自定义损失函数
class FocalLoss(nn.Module):
    """Focal Loss 用于处理类别不平衡问题"""
    
    def __init__(self, alpha=1.0, gamma=2.0, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss

# 训练函数
def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=10, device='cuda'):
    """训练模型"""
    
    model = model.to(device)
    
    # 记录训练过程
    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }
    
    best_val_acc = 0.0
    
    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            
            # 前向传播
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # 统计
            train_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            train_correct += predicted.eq(targets).sum().item()
            train_total += targets.size(0)
        
        train_loss = train_loss / train_total
        train_acc = train_correct / train_total
        
        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                
                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                val_correct += predicted.eq(targets).sum().item()
                val_total += targets.size(0)
        
        val_loss = val_loss / val_total
        val_acc = val_correct / val_total
        
        # 记录历史
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        # 打印进度
        print(f'Epoch {epoch+1}/{num_epochs}:')
        print(f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}')
        print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')
        
        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), 'best_model.pth')
    
    return history, best_val_acc

# 评估函数
def evaluate_model(model, test_loader, device='cuda'):
    """评估模型"""
    
    model = model.to(device)
    model.eval()
    
    all_targets = []
    all_predictions = []
    
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            
            all_targets.extend(targets.cpu().numpy())
            all_predictions.extend(predicted.cpu().numpy())
    
    accuracy = accuracy_score(all_targets, all_predictions)
    print(f"测试集准确率: {accuracy:.4f}")
    print("分类报告:")
    print(classification_report(all_targets, all_predictions))
    
    return accuracy

# 迁移学习
def transfer_learning(train_loader, val_loader, num_classes=10, device='cuda'):
    """使用迁移学习"""
    
    # 加载预训练模型
    model = models.resnet18(pretrained=True)
    
    # 冻结所有参数
    for param in model.parameters():
        param.requires_grad = False
    
    # 替换最后的全连接层
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    
    model = model.to(device)
    
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.fc.parameters(), lr=0.001, momentum=0.9)
    
    # 训练新添加的层
    print("训练新添加的层")
    history1, _ = train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=10, device=device)
    
    # 解冻置最后几层
    for param in model.layer4.parameters():
        param.requires_grad = True
    
    # 重新定义优化器，使用更低的学习率
    optimizer = optim.SGD([
        {'params': model.layer4.parameters(), 'lr': 0.0001},
        {'params': model.fc.parameters(), 'lr': 0.001}
    ], momentum=0.9)
    
    # 微调整个网络
    print("微调整个网络")
    history2, best_val_acc = train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=20, device=device)
    
    # 合并历史
    history = {
        'train_loss': history1['train_loss'] + history2['train_loss'],
        'train_acc': history1['train_acc'] + history2['train_acc'],
        'val_loss': history1['val_loss'] + history2['val_loss'],
        'val_acc': history1['val_acc'] + history2['val_acc']
    }
    
    return model, history, best_val_acc

# 可视化训练过程
def plot_history(history, title='Training History'):
    """可视化训练过程"""
    
    plt.figure(figsize=(12, 5))
    
    # 损失曲线
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='训练损失')
    plt.plot(history['val_loss'], label='验证损失')
    plt.title(f'{title} - 损失')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    # 准确率曲线
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='训练准确率')
    plt.plot(history['val_acc'], label='验证准确率')
    plt.title(f'{title} - 准确率')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

# 运行示例
def demo_pytorch_advanced():
    """演示PyTorch高级应用"""
    
    print("=== PyTorch高级应用演示 ===")
    
    # 检查GPU是否可用
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")
    
    # 创建模拟数据
    # 这里使用随机数据，实际应用中应该使用真实数据集
    # 为了演示，我们假设使用CIFAR-10形状的数据
    X_train = np.random.rand(1000, 3, 32, 32)
    y_train = np.random.randint(0, 10, 1000)
    X_val = np.random.rand(200, 3, 32, 32)
    y_val = np.random.randint(0, 10, 200)
    X_test = np.random.rand(200, 3, 32, 32)
    y_test = np.random.randint(0, 10, 200)
    
    # 定义数据转换
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # 创建数据集和数据加载器
    train_dataset = CustomDataset(X_train, y_train)
    val_dataset = CustomDataset(X_val, y_val)
    test_dataset = CustomDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # 1. 训练自定义CNN模型
    print("\n1. 训练自定义CNN模型")
    custom_model = CustomCNN(num_classes=10)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(custom_model.parameters(), lr=0.001)
    
    custom_history, custom_val_acc = train_model(
        custom_model, train_loader, val_loader, criterion, optimizer, num_epochs=10, device=device
    )
    
    custom_test_acc = evaluate_model(custom_model, test_loader, device=device)
    plot_history(custom_history, 'Custom CNN')
    
    # 2. 训练注意力模型
    print("\n2. 训练注意力模型")
    attention_model = AttentionCNN(num_classes=10)
    criterion = FocalLoss(alpha=1.0, gamma=2.0)
    optimizer = optim.Adam(attention_model.parameters(), lr=0.001)
    
    attention_history, attention_val_acc = train_model(
        attention_model, train_loader, val_loader, criterion, optimizer, num_epochs=10, device=device
    )
    
    attention_test_acc = evaluate_model(attention_model, test_loader, device=device)
    plot_history(attention_history, 'Attention CNN')
    
    # 3. 迁移学习
    print("\n3. 迁移学习")
    transfer_model, transfer_history, transfer_test_acc = transfer_learning(
        train_loader, val_loader, num_classes=10, device=device
    )
    
    plot_history(transfer_history, 'Transfer Learning')
    
    # 比较结果
    print("\n模型比较:")
    print(f"Custom CNN - 验证准确率: {custom_val_acc:.4f}, 测试准确率: {custom_test_acc:.4f}")
    print(f"Attention CNN - 验证准确率: {attention_val_acc:.4f}, 测试准确率: {attention_test_acc:.4f}")
    print(f"Transfer Learning - 测试准确率: {transfer_test_acc:.4f}")
    
    print("\n所有PyTorch高级应用演示完成!")
    return custom_model, attention_model, transfer_model

# 运行演示
if __name__ == "__main__":
    demo_pytorch_advanced()
```

## 3. 自动化机器学习

### 3.1 AutoML框架应用

```python
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Auto-Sklearn 示例
def demo_autosklearn(X_train, X_test, y_train, y_test):
    """使用Auto-Sklearn进行自动机器学习"""
    
    try:
        import autosklearn.classification
        import autosklearn.metrics
        import sklearn.model_selection
        
        print("=== Auto-Sklearn示例 ===")
        
        # 定义自动分类器
        automl = autosklearn.classification.AutoSklearnClassifier(
            time_left_for_this_task=120,  # 2分钟
            per_run_time_limit=30,       # 每个模型最多30秒
            ensemble_size=50,            # 集成大小
            ensemble_nbest=20,           # 选择最好的20个模型进行集成
            ml_memory_limit=3072,        # 内存限制(MB)
            seed=42
        )
        
        # 训练模型
        automl.fit(X_train, y_train)
        
        # 评估模型
        y_pred = automl.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Auto-Sklearn 准确率: {accuracy:.4f}")
        print("\n分类报告:")
        print(classification_report(y_test, y_pred))
        
        # 显示模型统计
        print("\n模型统计:")
        print(f"训练的模型数量: {len(automl.get_models_with_weights())}")
        
        # 显示排名前5的模型
        models_with_weights = automl.get_models_with_weights()
        print("\n前5个模型及其权重:")
        for i, (weight, model) in enumerate(models_with_weights[:5]):
            print(f"{i+1}. 权重: {weight:.4f}, 模型: {type(model).__name__}")
        
        return automl
        
    except ImportError:
        print("Auto-sklearn 未安装，跳过此示例")
        return None

# TPOT 示例
def demo_tpot(X_train, X_test, y_train, y_test):
    """使用TPOT进行自动机器学习"""
    
    try:
        from tpot import TPOTClassifier
        
        print("\n=== TPOT示例 ===")
        
        # 定义TPOT分类器
        tpot = TPOTClassifier(
            generations=5,        # 进化代数
            population_size=20,   # 种群大小
            offspring_size=5,     # 每代生成的后代数量
            mutation_rate=0.9,    # 变异率
            crossover_rate=0.1,   # 交叉率
            scoring='accuracy', # 评估指标
            cv=5,                # 交叉验证折数
            n_jobs=-1,           # 并行工作数
            random_state=42,
            verbosity=2           # 详细程度
        )
        
        # 训练模型
        tpot.fit(X_train, y_train)
        
        # 评估模型
        accuracy = tpot.score(X_test, y_test)
        print(f"\nTPOT 准确率: {accuracy:.4f}")
        
        # 导出最佳模型代码
        print("\n最佳模型代码:")
        tpot.export('tpot_best_model.py')
        
        return tpot
        
    except ImportError:
        print("TPOT 未安装，跳过此示例")
        return None

# AutoKeras 示例
def demo_autokeras():
    """使用AutoKeras进行自动机器学习"""
    
    try:
        import autokeras as ak
        import tensorflow as tf
        
        print("\n=== AutoKeras示例 ===")
        
        # 加载数据集
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
        
        # 数据预处理
        x_train = x_train.astype('float32') / 255.0
        x_test = x_test.astype('float32') / 255.0
        
        # 定义搜索空间
        clf = ak.ImageClassifier(
            max_trials=10,        # 最多尝试的模型数量
            objective='val_accuracy' # 优化目标
        )
        
        # 搜索最佳模型
        clf.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=10)
        
        # 评估模型
        accuracy = clf.evaluate(x_test, y_test)
        print(f"\nAutoKeras 准确率: {accuracy[1]:.4f}")
        
        # 导出最佳模型
        model = clf.export_model()
        model.summary()
        
        return clf
        
    except ImportError:
        print("AutoKeras 未安装，跳过此示例")
        return None

# LightAutoML 示例
def demo_lightautoml(X_train, X_test, y_train, y_test):
    """使用LightAutoML进行自动机器学习"""
    
    try:
        from lightautoml.automl.presets.tabular_presets import TabularAutoML
        from lightautoml.tasks import Task
        from lightautoml.dataset.roles import DatetimeRole
        from lightautoml.dataset.roles import TargetRole
        
        print("\n=== LightAutoML示例 ===")
        
        # 创建任务
        task = Task('binary')  # 假设是二分类任务
        
        # 创建AutoML模型
        automl = TabularAutoML(
            task=task,
            timeout=600,         # 超时时间(秒)
            cpu_limit=4,        # CPU限制
            general_params={'use_algos': ['linear_l2', 'lgb', 'cb']},
            reader_params={'n_jobs': 4},
            tuning_params={'max_tuning_time': 30}
        )
        
        # 将数据转换为DataFrame格式
        train_df = pd.DataFrame(X_train)
        train_df['target'] = y_train
        test_df = pd.DataFrame(X_test)
        
        # 训练模型
        oof_pred = automl.fit_predict(train_df, roles={'target': 'target'})
        
        # 预测
        test_pred = automl.predict(test_df)
        y_pred = (test_pred.data[:, 0] > 0.5).astype(int)
        
        # 评估
        accuracy = accuracy_score(y_test, y_pred)
        print(f"LightAutoML 准确率: {accuracy:.4f}")
        
        return automl
        
    except ImportError:
        print("LightAutoML 未安装，跳过此示例")
        return None

# 自定义AutoML框架
class SimpleAutoML:
    """简单的AutoML框架实现"""
    
    def __init__(self, task_type='classification', max_time=300, n_trials=10):
        self.task_type = task_type
        self.max_time = max_time
        self.n_trials = n_trials
        self.best_model = None
        self.best_score = None
        self.models = []
        self.scores = []
    
    def fit(self, X, y):
        """训练AutoML模型"""
        
        print(f"开始{self.task_type}任务的AutoML训练")
        
        # 定义候选模型
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.naive_bayes import GaussianNB
        from sklearn.model_selection import cross_val_score
        
        if self.task_type == 'classification':
            models = [
                ('RandomForest', RandomForestClassifier(n_estimators=100, random_state=42)),
                ('GradientBoosting', GradientBoostingClassifier(random_state=42)),
                ('LogisticRegression', LogisticRegression(max_iter=1000, random_state=42)),
                ('SVC', SVC(probability=True, random_state=42)),
                ('DecisionTree', DecisionTreeClassifier(random_state=42)),
                ('KNN', KNeighborsClassifier()),
                ('GaussianNB', GaussianNB())
            ]
        else:
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.linear_model import LinearRegression, Ridge
            from sklearn.tree import DecisionTreeRegressor
            from sklearn.neighbors import KNeighborsRegressor
            from sklearn.svm import SVR
            
            models = [
                ('RandomForest', RandomForestRegressor(n_estimators=100, random_state=42)),
                ('GradientBoosting', GradientBoostingRegressor(random_state=42)),
                ('LinearRegression', LinearRegression()),
                ('Ridge', Ridge(random_state=42)),
                ('DecisionTree', DecisionTreeRegressor(random_state=42)),
                ('KNN', KNeighborsRegressor()),
                ('SVR', SVR())
            ]
        
        # 评估每个模型
        for name, model in models:
            if self.task_type == 'classification':
                scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
                avg_score = scores.mean()
            else:
                scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
                avg_score = -scores.mean()  # 转换为正值
        
            print(f"{name}: 平均得分: {avg_score:.4f}")
            
            self.models.append((name, model))
            self.scores.append(avg_score)
            
            # 更新最佳模型
            if self.best_score is None or avg_score > self.best_score:
                self.best_score = avg_score
                self.best_model = (name, model)
        
        print(f"\n最佳模型: {self.best_model[0]}, 得分: {self.best_score:.4f}")
        
        # 训练最佳模型
        _, best_model = self.best_model
        best_model.fit(X, y)
        self.best_model = (self.best_model[0], best_model)
    
    def predict(self, X):
        """使用最佳模型进行预测"""
        if self.best_model is None:
            raise ValueError("模型尚未训练")
        
        _, best_model = self.best_model
        return best_model.predict(X)
    
    def predict_proba(self, X):
        """使用最佳模型预测概率"""
        if self.best_model is None:
            raise ValueError("模型尚未训练")
        
        _, best_model = self.best_model
        if hasattr(best_model, 'predict_proba'):
            return best_model.predict_proba(X)
        else:
            raise ValueError("模型不支持概率预测")

# 运行示例
def demo_automl_frameworks():
    """演示AutoML框架"""
    
    print("=== AutoML框架演示 ===")
    
    # 生成示例数据
    X, y = datasets.make_classification(
        n_samples=1000, 
        n_features=20, 
        n_informative=10, 
        n_redundant=5, 
        random_state=42
    )
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 1. Auto-Sklearn示例
    autosklearn_model = demo_autosklearn(X_train, X_test, y_train, y_test)
    
    # 2. TPOT示例
    tpot_model = demo_tpot(X_train, X_test, y_train, y_test)
    
    # 3. AutoKeras示例
    autokeras_model = demo_autokeras()
    
    # 4. LightAutoML示例
    lightautoml_model = demo_lightautoml(X_train, X_test, y_train, y_test)
    
    # 5. 自定义AutoML框架
    print("\n=== 自定义AutoML框架 ===")
    simple_automl = SimpleAutoML(task_type='classification', n_trials=7)
    simple_automl.fit(X_train, y_train)
    y_pred = simple_automl.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"自定义AutoML测试准确率: {accuracy:.4f}")
    print("\n分类报告:")
    print(classification_report(y_test, y_pred))
    
    return {
        'autosklearn': autosklearn_model,
        'tpot': tpot_model,
        'autokeras': autokeras_model,
        'lightautoml': lightautoml_model,
        'simple_automl': simple_automl
    }

# 运行演示
if __name__ == "__main__":
    automl_models = demo_automl_frameworks()
    print("\n所有AutoML框架演示完成!")
```

这份Python机器学习高级指南涵盖了scikit-learn高级应用、集成学习高级技术、深度学习框架集成（TensorFlow和PyTorch）以及自动化机器学习（AutoML）等高级主题。通过这份指南，您可以掌握构建和优化复杂机器学习模型的核心技能，应用集成学习提高模型性能，利用深度学习框架解决复杂问题，并使用AutoML技术自动化机器学习工作流程。