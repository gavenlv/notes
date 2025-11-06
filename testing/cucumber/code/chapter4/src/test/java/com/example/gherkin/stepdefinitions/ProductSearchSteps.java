package com.example.gherkin.stepdefinitions;

import com.example.gherkin.model.Product;
import com.example.gherkin.service.ProductService;
import com.example.gherkin.transformer.ProductTransformer;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.cucumber.java.en.And;
import io.cucumber.datatable.DataTable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * 产品搜索功能的步骤定义
 */
@SpringBootTest
public class ProductSearchSteps {
    
    @Autowired
    private ProductService productService;
    
    private List<Product> searchResults;
    private ProductTransformer transformer = new ProductTransformer();
    
    @Given("系统中有以下产品")
    public void thereAreFollowingProducts(DataTable dataTable) {
        List<Map<String, String>> products = dataTable.asMaps();
        
        for (Map<String, String> productData : products) {
            Product product = Product.builder()
                    .name(productData.get("名称"))
                    .description(productData.get("描述"))
                    .price(new BigDecimal(productData.get("价格")))
                    .category(productData.get("类别"))
                    .brand(productData.get("品牌"))
                    .stockQuantity(Integer.parseInt(productData.get("库存数量")))
                    .available(Boolean.parseBoolean(productData.get("可用")))
                    .sku(productData.get("SKU"))
                    .build();
            
            productService.createProduct(product);
        }
    }
    
    @When("用户搜索名称包含 {string} 的产品")
    public void userSearchesForProductsWithNameContaining(String name) {
        searchResults = productService.searchProductsByName(name);
    }
    
    @When("用户搜索类别为 {string} 的产品")
    public void userSearchesForProductsWithCategory(String category) {
        searchResults = productService.searchProductsByCategory(category);
    }
    
    @When("用户搜索品牌为 {string} 的产品")
    public void userSearchesForProductsWithBrand(String brand) {
        searchResults = productService.searchProductsByBrand(brand);
    }
    
    @When("用户搜索价格在 {string} 到 {string} 之间的产品")
    public void userSearchesForProductsWithPriceBetween(String minPrice, String maxPrice) {
        BigDecimal min = minPrice.isEmpty() ? null : new BigDecimal(minPrice);
        BigDecimal max = maxPrice.isEmpty() ? null : new BigDecimal(maxPrice);
        searchResults = productService.searchProductsByPriceRange(min, max);
    }
    
    @When("用户搜索有库存的产品")
    public void userSearchesForInStockProducts() {
        searchResults = productService.searchInStockProducts();
    }
    
    @When("用户使用以下条件搜索产品")
    public void userSearchesWithFollowingConditions(DataTable dataTable) {
        Map<String, String> searchCriteria = dataTable.asMap();
        
        String name = searchCriteria.get("名称");
        String category = searchCriteria.get("类别");
        String brand = searchCriteria.get("品牌");
        String minPrice = searchCriteria.get("最低价格");
        String maxPrice = searchCriteria.get("最高价格");
        
        BigDecimal min = minPrice != null && !minPrice.isEmpty() ? 
                         new BigDecimal(minPrice) : null;
        BigDecimal max = maxPrice != null && !maxPrice.isEmpty() ? 
                         new BigDecimal(maxPrice) : null;
        
        searchResults = productService.searchProducts(name, category, brand, min, max);
    }
    
    @When("用户使用场景大纲参数搜索产品: 名称包含 {string}, 类别 {string}, 品牌 {string}, 价格范围 {string} 到 {string}")
    public void userSearchesWithScenarioOutlineParameters(String name, String category, String brand, String minPrice, String maxPrice) {
        String searchName = name.isEmpty() ? null : name;
        String searchCategory = category.isEmpty() ? null : category;
        String searchBrand = brand.isEmpty() ? null : brand;
        
        BigDecimal min = minPrice.isEmpty() ? null : new BigDecimal(minPrice);
        BigDecimal max = maxPrice.isEmpty() ? null : new BigDecimal(maxPrice);
        
        searchResults = productService.searchProducts(searchName, searchCategory, searchBrand, min, max);
    }
    
    @When("用户使用转换器搜索产品: 名称包含 {string}, 类别 {productCategory}, 品牌 {productBrand}, 价格 {pricePredicate}")
    public void userSearchesWithTransformerParameters(String name, String category, String brand, ProductTransformer.PricePredicate pricePredicate) {
        String searchName = name.isEmpty() ? null : name;
        String searchCategory = category.isEmpty() ? null : category;
        String searchBrand = brand.isEmpty() ? null : brand;
        
        // 使用价格谓词确定价格范围
        BigDecimal minPrice = null;
        BigDecimal maxPrice = null;
        
        if (pricePredicate != null) {
            switch (pricePredicate.getOperator()) {
                case "=":
                    minPrice = pricePredicate.getValue();
                    maxPrice = pricePredicate.getValue();
                    break;
                case ">":
                case ">=":
                    minPrice = pricePredicate.getValue();
                    break;
                case "<":
                case "<=":
                    maxPrice = pricePredicate.getValue();
                    break;
            }
        }
        
        searchResults = productService.searchProducts(searchName, searchCategory, searchBrand, minPrice, maxPrice);
    }
    
    @When("用户使用转换器搜索产品: 类别列表 {categoryList}, 品牌列表 {brandList}")
    public void userSearchesWithCategoryAndBrandLists(List<String> categories, List<String> brands) {
        // 这里简化实现，只使用第一个类别和品牌进行搜索
        String category = categories.isEmpty() ? null : categories.get(0);
        String brand = brands.isEmpty() ? null : brands.get(0);
        
        searchResults = productService.searchProducts(null, category, brand, null, null);
    }
    
    @When("用户使用价格范围 {priceRange} 搜索产品")
    public void userSearchesWithPriceRange(BigDecimal[] priceRange) {
        BigDecimal minPrice = priceRange.length > 0 ? priceRange[0] : null;
        BigDecimal maxPrice = priceRange.length > 1 ? priceRange[1] : null;
        
        searchResults = productService.searchProductsByPriceRange(minPrice, maxPrice);
    }
    
    @Then("搜索结果应包含 {int} 个产品")
    public void searchResultsShouldContainProducts(int count) {
        assertThat(searchResults).hasSize(count);
    }
    
    @Then("搜索结果应包含产品 {string}")
    public void searchResultsShouldContainProduct(String productName) {
        assertThat(searchResults)
                .extracting(Product::getName)
                .contains(productName);
    }
    
    @Then("搜索结果不应包含产品 {string}")
    public void searchResultsShouldNotContainProduct(String productName) {
        assertThat(searchResults)
                .extracting(Product::getName)
                .doesNotContain(productName);
    }
    
    @Then("搜索结果中的所有产品都属于 {string} 类别")
    public void allProductsInSearchResultsShouldBeOfCategory(String category) {
        assertThat(searchResults)
                .allMatch(product -> product.isInCategory(category));
    }
    
    @Then("搜索结果中的所有产品都是 {string} 品牌")
    public void allProductsInSearchResultsShouldBeOfBrand(String brand) {
        assertThat(searchResults)
                .allMatch(product -> brand.equals(product.getBrand()));
    }
    
    @Then("搜索结果中的所有产品价格都在 {string} 到 {string} 之间")
    public void allProductsInSearchResultsShouldHavePriceBetween(String minPrice, String maxPrice) {
        BigDecimal min = new BigDecimal(minPrice);
        BigDecimal max = new BigDecimal(maxPrice);
        
        assertThat(searchResults)
                .allMatch(product -> product.isPriceInRange(min, max));
    }
    
    @Then("搜索结果中的所有产品都有库存")
    public void allProductsInSearchResultsShouldBeInStock() {
        assertThat(searchResults)
                .allMatch(Product::isInStock);
    }
    
    @Then("搜索结果中的所有产品名称都包含 {string}")
    public void allProductsInSearchResultsShouldHaveNameContaining(String name) {
        assertThat(searchResults)
                .allMatch(product -> product.getName().toLowerCase().contains(name.toLowerCase()));
    }
    
    @Then("搜索结果应包含以下产品")
    public void searchResultsShouldContainFollowingProducts(DataTable dataTable) {
        List<String> expectedProductNames = dataTable.asList();
        
        assertThat(searchResults)
                .extracting(Product::getName)
                .containsAll(expectedProductNames);
    }
    
    @And("系统中已存在产品 {product}")
    public void productExistsInSystem(Product product) {
        productService.createProduct(product);
    }
    
    @And("搜索结果应包含产品 {product}")
    public void searchResultsShouldContainProduct(Product product) {
        assertThat(searchResults)
                .anyMatch(p -> p.getName().equals(product.getName()) && 
                             p.getPrice().equals(product.getPrice()));
    }
}