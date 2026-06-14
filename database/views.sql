SET search_path = public, pg_catalog;

CREATE OR REPLACE VIEW filmes_publicos AS
SELECT
    f.film_id,
    f.title,
    f.release_year,
    l.name AS language,
    f.rating,
    f.length,
    c.name AS category
FROM film f
JOIN language l ON l.language_id = f.language_id
LEFT JOIN film_category fc ON fc.film_id = f.film_id
LEFT JOIN category c ON c.category_id = fc.category_id;

CREATE OR REPLACE VIEW filmes_mais_alugados AS
SELECT
    f.title,
    c.name AS category,
    COUNT(r.rental_id) AS total_alugueis
FROM rental r
JOIN inventory i ON i.inventory_id = r.inventory_id
JOIN film f ON f.film_id = i.film_id
LEFT JOIN film_category fc ON fc.film_id = f.film_id
LEFT JOIN category c ON c.category_id = fc.category_id
GROUP BY f.title, c.name
ORDER BY total_alugueis DESC;

CREATE OR REPLACE VIEW clientes_por_cidade AS
SELECT
    ci.city,
    co.country,
    COUNT(c.customer_id) AS total_clientes
FROM customer c
JOIN address a ON a.address_id = c.address_id
JOIN city ci ON ci.city_id = a.city_id
JOIN country co ON co.country_id = ci.country_id
GROUP BY ci.city, co.country
ORDER BY total_clientes DESC;

CREATE OR REPLACE VIEW vendas_por_categoria AS
SELECT
    cat.name AS categoria,
    ROUND(SUM(p.amount)::numeric, 2) AS receita_total,
    COUNT(DISTINCT r.rental_id) AS total_alugueis
FROM payment p
JOIN rental r ON r.rental_id = p.rental_id
JOIN inventory i ON i.inventory_id = r.inventory_id
JOIN film f ON f.film_id = i.film_id
JOIN film_category fc ON fc.film_id = f.film_id
JOIN category cat ON cat.category_id = fc.category_id
GROUP BY cat.name
ORDER BY receita_total DESC;

CREATE OR REPLACE VIEW vendas_por_mes AS
SELECT
    DATE_TRUNC('month', payment_date)::date AS mes,
    ROUND(SUM(amount)::numeric, 2) AS receita_total,
    COUNT(*) AS total_pagamentos
FROM payment
GROUP BY DATE_TRUNC('month', payment_date)::date
ORDER BY mes;

CREATE OR REPLACE VIEW receita_por_loja AS
SELECT
    s.store_id,
    ci.city,
    co.country,
    ROUND(SUM(p.amount)::numeric, 2) AS receita_total
FROM payment p
JOIN staff st ON st.staff_id = p.staff_id
JOIN store s ON s.store_id = st.store_id
JOIN address a ON a.address_id = s.address_id
JOIN city ci ON ci.city_id = a.city_id
JOIN country co ON co.country_id = ci.country_id
GROUP BY s.store_id, ci.city, co.country
ORDER BY receita_total DESC;
