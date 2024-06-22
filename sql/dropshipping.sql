
select sum(amount) from facebook_ads fa where fa.payment_method = 'Wallet';

-- total wallet reloads

select sum(amount) from facebook_ads fa where fa.payment_type = 'WALLET_RELOAD';

-- total cost for customer acquisition

select sum(amount) from facebook_ads fa where fa.payment_type != 'WALLET_RELOAD';

-- total cost from facebook ads report

select SUM("Amount spent (INR)") from facebook_ads_performance_new fap;

select SUM("Amount spent (INR)") from facebook_ads_performance_new fap where "Reporting starts" >= '2024-03-28' and "Reporting ends" <= '2024-04-21';

select sum("Tentative Margin") from  roposo_orders ro where ro."Latest Status" = 'delivered';

select sum("Tentative Margin") from  roposo_orders ro where ro."Latest Status" IN ('pendingdelivery','pendingshipment');


select sum(fap."Amount spent (INR)") from facebook_ads_performance_new fap where "Reporting starts" = '2024-05-01' and "Reporting ends" = '2024-05-01';


CREATE TABLE dropshipping.facebook_ads_performance_new (
	"Campaign name" varchar(50) NULL,
	"Ad set name" varchar(50) NULL,
	"Ad name" varchar(50) NULL,
	"Ads" varchar(50) NULL,
	"Reporting starts" date NULL,
	"Reporting ends" date NULL,
	"Reach" int4 NULL,
	"Impressions" int4 NULL,
	"Link clicks" int4 NULL,
	"CTR (link click-through rate)" float4 NULL,
	"Adds to cart" int4 NULL,
	"Checkouts initiated" int4 NULL,
	"Purchases" int4 NULL,
	"CPM (cost per 1,000 impressions)" float4 NULL,
	"CPC (cost per link click)" float4 NULL,
	"Cost per purchase" float4 NULL,
	"Cost per result" float4 NULL,
	"Purchase ROAS (return on ad spend)" float4 NULL,
	"Amount spent (INR)" float4 NULL,
	"CTR (all)" float4 NULL,
	"Follows or likes" varchar(50) NULL,
	"Post comments" varchar(50) NULL,
	"Post engagements" int4 NULL,
	"Post reactions" int4 NULL,
	"Post shares" int4 NULL,
	"Video plays at 25%" int4 NULL,
	"Video plays at 50%" int4 NULL,
	"Video plays at 75%" int4 NULL,
	"Video plays at 95%" int4 NULL,
	"Video plays at 100%" int4 NULL,
	"Video average play time" int4 NULL,
	"Attribution setting" varchar(50) NULL,
	"Result Type" varchar(50) NULL,
	"Starts" date NULL,
	"Ends" varchar(50) NULL,
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	CONSTRAINT facebook_ads_performance_pk4 PRIMARY KEY (id)
);




-- all campaigns
select distinct "Campaign name" from facebook_ads_performance_new fapn;


-- juice blender with only one ad each

select * from facebook_ads_performance_new fapn where "Campaign name" = 'Juice Blender' and "Reporting starts" != '2024-05-01' and "Reporting ends" != '2024-05-01';


-- juice blender tiktok with only one ad each

select * from facebook_ads_performance_new fapn where "Campaign name" = 'Juice Blender – Tiktok' and "Reporting starts" != '2024-05-01' and "Reporting ends" != '2024-05-01';


-- juice blender with multiple ads

select * from facebook_ads_performance_new fapn where "Campaign name" = 'Juice Blender' and "Reporting starts" = '2024-05-01' and "Reporting ends" = '2024-05-01'









